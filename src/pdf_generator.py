import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd

try:
    from fpdf import FPDF  # fpdf2
    import qrcode
except ModuleNotFoundError as e:
    FPDF = None  # type: ignore
    qrcode = None  # type: ignore
    _PDF_IMPORT_ERROR = e
else:
    _PDF_IMPORT_ERROR = None

try:
    from src.database import get_database
except ModuleNotFoundError:
    from database import get_database


_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _resolve_project_path(path: str) -> str:
    if not path:
        return path
    if os.path.isabs(path):
        return path
    return os.path.join(_PROJECT_ROOT, path)


@dataclass
class CompanyInfo:
    name: str
    vat: str
    address: str
    email: str
    phone: str
    logo_path: Optional[str] = None


def get_company_info() -> CompanyInfo:
    return CompanyInfo(
        name=os.getenv("COMPANY_NAME", "Firma - Ferragens e Serralharia"),
        vat=os.getenv("COMPANY_VAT", ""),
        address=os.getenv("COMPANY_ADDRESS", ""),
        email=os.getenv("COMPANY_EMAIL", ""),
        phone=os.getenv("COMPANY_PHONE", ""),
        logo_path=os.getenv("COMPANY_LOGO_PATH", "data/logo.png"),
    )


def _require_pdf_deps() -> None:
    if _PDF_IMPORT_ERROR is not None or FPDF is None or qrcode is None:
        raise ModuleNotFoundError(
            "Dependências de PDF em falta. Instala com: pip install -r requirements.txt"
        ) from _PDF_IMPORT_ERROR


if FPDF is not None:

    class _Pdf(FPDF):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._font_regular = ("Helvetica", "")
            self._font_bold = ("Helvetica", "B")
            self._unicode_enabled = False
            self._try_enable_unicode_fonts()

        def _try_enable_unicode_fonts(self) -> None:
            # fpdf2 core fonts (Helvetica, etc.) are not Unicode and will fail on symbols like "€".
            # On Windows, we can usually rely on system fonts.
            fonts_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
            candidates = [
                (os.path.join(fonts_dir, "segoeui.ttf"), os.path.join(fonts_dir, "segoeuib.ttf")),
                (os.path.join(fonts_dir, "arial.ttf"), os.path.join(fonts_dir, "arialbd.ttf")),
                (os.path.join(fonts_dir, "calibri.ttf"), os.path.join(fonts_dir, "calibrib.ttf")),
            ]

            env_regular = os.getenv("PDF_FONT_REGULAR")
            env_bold = os.getenv("PDF_FONT_BOLD")
            if env_regular:
                candidates.insert(0, (_resolve_project_path(env_regular), _resolve_project_path(env_bold or "")))

            for regular_path, bold_path in candidates:
                if not regular_path or not os.path.exists(regular_path):
                    continue

                self.add_font("FirmaUnicode", "", regular_path)

                if bold_path and os.path.exists(bold_path):
                    self.add_font("FirmaUnicodeBold", "", bold_path)
                    self._font_bold = ("FirmaUnicodeBold", "")
                else:
                    self._font_bold = ("FirmaUnicode", "")

                self._font_regular = ("FirmaUnicode", "")
                self._unicode_enabled = True
                return

        def set_font_regular(self, size: int) -> None:
            family, style = self._font_regular
            self.set_font(family, style, size)

        def set_font_bold(self, size: int) -> None:
            family, style = self._font_bold
            self.set_font(family, style, size)

        def header(self):
            info = get_company_info()
            logo_path = _resolve_project_path(info.logo_path or "")
            if logo_path and os.path.exists(logo_path):
                self.image(logo_path, x=10, y=8, w=25)

            self.set_font_bold(12)
            self.cell(0, 8, info.name, ln=True, align="R")
            self.set_font_regular(9)
            if info.vat:
                self.cell(0, 5, f"NIF: {info.vat}", ln=True, align="R")
            if info.address:
                self.multi_cell(0, 4, info.address, align="R")
            if info.email or info.phone:
                self.cell(0, 5, f"{info.email}  {info.phone}".strip(), ln=True, align="R")
            self.ln(5)

else:
    _Pdf = None  # type: ignore


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _money(value: float) -> str:
    return f"€{value:,.2f}"


def _get_invoice_data(fatura_id: int):
    db = get_database()

    header_q = """
    SELECT
        f.id,
        f.num_fatura,
        f.data_emissao,
        f.vencimento,
        f.metodo_pagamento,
        f.status,
        f.valor_base,
        f.valor_iva,
        f.valor_total,
        f.valor_pago,
        f.saldo,
        c.nome AS cliente_nome,
        c.nif AS cliente_nif,
        c.email AS cliente_email,
        c.contacto AS cliente_contacto,
        c.morada AS cliente_morada
    FROM faturas f
    JOIN clientes c ON f.cliente_id = c.id
    WHERE f.id = %s
    """

    itens_q = """
    SELECT
        descricao,
        quantidade,
        preco_unitario,
        taxa_iva,
        valor_linha_base,
        valor_linha_iva,
        valor_linha_total
    FROM itens_fatura
    WHERE fatura_id = %s
    ORDER BY id
    """

    header = db.execute_query(header_q, (fatura_id,))
    itens = db.execute_query(itens_q, (fatura_id,))

    if header.empty:
        raise ValueError("Fatura não encontrada")

    return header.iloc[0].to_dict(), itens


def generate_invoice_pdf(fatura_id: int, output_dir: str = "data/pdfs") -> str:
    """Gera PDF da fatura e devolve o caminho do ficheiro."""
    _require_pdf_deps()
    output_dir = _resolve_project_path(output_dir)
    _ensure_dir(output_dir)

    header, itens = _get_invoice_data(fatura_id)

    pdf = _Pdf(orientation="P", unit="mm", format="A4")  # type: ignore[misc]
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font_bold(14)
    pdf.cell(0, 8, "FATURA", ln=True)

    pdf.set_font_regular(10)
    pdf.cell(0, 6, f"Nº: {header['num_fatura']}", ln=True)
    pdf.cell(0, 6, f"Data emissão: {header['data_emissao']}", ln=True)
    if header.get("vencimento") is not None:
        pdf.cell(0, 6, f"Vencimento: {header['vencimento']}", ln=True)
    pdf.ln(2)

    pdf.set_font_bold(11)
    pdf.cell(0, 6, "Cliente", ln=True)
    pdf.set_font_regular(10)
    pdf.cell(0, 5, str(header.get("cliente_nome") or ""), ln=True)
    nif = header.get("cliente_nif")
    if nif:
        pdf.cell(0, 5, f"NIF: {nif}", ln=True)
    morada = header.get("cliente_morada")
    if morada:
        pdf.multi_cell(0, 4, str(morada))
    pdf.ln(2)

    # Tabela itens
    pdf.set_font_bold(10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 7, "Descrição", border=1, fill=True)
    pdf.cell(20, 7, "Qtd", border=1, align="R", fill=True)
    pdf.cell(30, 7, "Preço", border=1, align="R", fill=True)
    pdf.cell(0, 7, "Total", border=1, align="R", fill=True, ln=True)

    pdf.set_font_regular(10)
    for _, row in itens.iterrows():
        pdf.cell(100, 7, str(row["descricao"])[:55], border=1)
        pdf.cell(20, 7, f"{float(row['quantidade']):.2f}", border=1, align="R")
        pdf.cell(30, 7, _money(float(row["preco_unitario"])), border=1, align="R")
        pdf.cell(0, 7, _money(float(row["valor_linha_total"])), border=1, align="R", ln=True)

    pdf.ln(4)

    pdf.set_font_bold(11)
    pdf.cell(0, 6, "Resumo", ln=True)
    pdf.set_font_regular(10)
    pdf.cell(0, 5, f"Base: {_money(float(header['valor_base']))}", ln=True)
    pdf.cell(0, 5, f"IVA: {_money(float(header['valor_iva']))}", ln=True)
    pdf.cell(0, 5, f"Total: {_money(float(header['valor_total']))}", ln=True)
    pdf.cell(0, 5, f"Pago: {_money(float(header['valor_pago']))}", ln=True)
    pdf.cell(0, 5, f"Saldo: {_money(float(header['saldo']))}", ln=True)

    # QR Code (placeholder): referência de pagamento
    referencia = f"FATURA:{header['num_fatura']}|TOTAL:{float(header['valor_total']):.2f}"
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(referencia)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    qr_path = os.path.join(output_dir, f"qr_{header['num_fatura'].replace('/', '_')}.png")
    img.save(qr_path)

    pdf.ln(6)
    pdf.set_font_regular(9)
    pdf.cell(0, 5, "QR (referência):", ln=True)
    pdf.image(qr_path, x=10, y=pdf.get_y(), w=35)

    out_path = os.path.join(output_dir, f"fatura_{header['num_fatura'].replace('/', '_')}.pdf")
    pdf.output(out_path)
    return out_path


def generate_orcamento_pdf(orcamento_id: int, output_dir: str = "data/pdfs") -> str:
    """Gera PDF simples do orçamento."""
    _require_pdf_deps()
    output_dir = _resolve_project_path(output_dir)
    _ensure_dir(output_dir)
    db = get_database()

    q = """
    SELECT
        o.id,
        o.data_orcamento,
        o.custo_material,
        o.custo_mao_obra,
        o.outros_custos,
        o.custo_total,
        o.margem_percentual,
        o.preco_venda,
        o.status,
        c.nome AS cliente,
        c.nif AS cliente_nif,
        c.morada AS cliente_morada,
        tp.nome AS tipo_produto,
        p.codigo,
        p.descricao
    FROM orcamentos o
    JOIN clientes c ON o.cliente_id = c.id
    JOIN produtos p ON o.produto_id = p.id
    JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
    WHERE o.id = %s
    """

    df = db.execute_query(q, (orcamento_id,))
    if df.empty:
        raise ValueError("Orçamento não encontrado")

    r = df.iloc[0].to_dict()

    pdf = _Pdf(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font_bold(14)
    pdf.cell(0, 8, "ORÇAMENTO", ln=True)

    pdf.set_font_regular(10)
    pdf.cell(0, 6, f"ID: {r['id']}", ln=True)
    pdf.cell(0, 6, f"Data: {r['data_orcamento']}", ln=True)
    pdf.ln(2)

    pdf.set_font_bold(11)
    pdf.cell(0, 6, "Cliente", ln=True)
    pdf.set_font_regular(10)
    pdf.cell(0, 5, str(r.get("cliente") or ""), ln=True)
    if r.get("cliente_nif"):
        pdf.cell(0, 5, f"NIF: {r['cliente_nif']}", ln=True)
    if r.get("cliente_morada"):
        pdf.multi_cell(0, 4, str(r["cliente_morada"]))
    pdf.ln(2)

    pdf.set_font_bold(11)
    pdf.cell(0, 6, "Produto", ln=True)
    pdf.set_font_regular(10)
    pdf.cell(0, 5, f"{r['tipo_produto']} - {r['codigo']}", ln=True)
    if r.get("descricao"):
        pdf.multi_cell(0, 4, str(r["descricao"]))
    pdf.ln(2)

    pdf.set_font_bold(11)
    pdf.cell(0, 6, "Custos & Preço", ln=True)
    pdf.set_font_regular(10)
    pdf.cell(0, 5, f"Custo material: {_money(float(r['custo_material']))}", ln=True)
    pdf.cell(0, 5, f"Custo mão de obra: {_money(float(r['custo_mao_obra']))}", ln=True)
    pdf.cell(0, 5, f"Outros custos: {_money(float(r['outros_custos']))}", ln=True)
    pdf.cell(0, 5, f"Custo total: {_money(float(r['custo_total']))}", ln=True)
    pdf.cell(0, 5, f"Margem: {float(r['margem_percentual']):.2f}%", ln=True)
    pdf.set_font_bold(11)
    pdf.cell(0, 7, f"Preço: {_money(float(r['preco_venda']))}", ln=True)

    out_path = os.path.join(output_dir, f"orcamento_{int(r['id'])}.pdf")
    pdf.output(out_path)
    return out_path

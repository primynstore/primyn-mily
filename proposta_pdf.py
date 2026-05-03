# ═══════════════════════════════════════════════
# PRIMYN STUDIO — GERADOR DE PROPOSTAS PDF
# ═══════════════════════════════════════════════

import os
from datetime import datetime, timedelta
from fpdf import FPDF


class PropostaPrimyn(FPDF):
    """PDF premium da Primyn Studio"""
    
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(180, 150, 50)
        self.cell(0, 10, "PRIMYN STUDIO", align="R")
        self.ln(5)
        self.set_draw_color(180, 150, 50)
        self.line(10, 15, 200, 15)
        self.ln(10)
    
    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, "primyn.com | @primyn.store | ola@primyn.com", align="C")
        self.ln(4)
        self.cell(0, 5, "Cada detalhe importa.", align="C")


def gerar_proposta(dados):
    """Gera proposta em PDF com dados do lead."""
    pdf = PropostaPrimyn()
    pdf.set_auto_page_break(auto=True, margin=25)
    
    nome = dados.get("nome", "Cliente")
    nome_primeiro = nome.split()[0] if nome else "Cliente"
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    validade = (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")
    
    # CAPA
    pdf.add_page()
    pdf.ln(40)
    
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(0, 15, "PROPOSTA", align="C")
    pdf.ln(12)
    
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(180, 150, 50)
    pdf.cell(0, 10, "PERSONALIZADA", align="C")
    pdf.ln(20)
    
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, f"Preparada para: {nome}", align="C")
    pdf.ln(8)
    pdf.cell(0, 8, f"Data: {data_hoje}", align="C")
    pdf.ln(8)
    pdf.cell(0, 8, f"Validade: {validade}", align="C")
    
    # APRESENTAÇÃO
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(0, 10, "Sobre a Primyn Studio")
    pdf.ln(12)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    
    texto_apresentacao = (
        "A Primyn Studio e uma marca especializada em papelaria de luxo e materiais "
        "graficos premium. Trabalhamos com os melhores papeis, texturas e acabamentos "
        "disponiveis no mercado para criar pecas que traduzem o posicionamento da sua marca "
        "com sofisticacao e elegancia.\n\n"
        "Cada projeto e tratado de forma unica. Desde a escolha do material ate o acabamento "
        "final, garantimos que o resultado reflita exatamente a identidade e o nivel de "
        "excelencia que a sua marca merece.\n\n"
        "Nossos diferenciais:\n\n"
        "- Papeis premium importados e nacionais de alta gramatura\n"
        "- Acabamentos artesanais: hot stamping, relevo, empastamento\n"
        "- Atendimento consultivo e personalizado\n"
        "- Producao com controle de qualidade rigoroso\n"
        "- Prazo medio de 5 a 8 dias uteis"
    )
    
    pdf.multi_cell(0, 6, texto_apresentacao)
    
    # DETALHES DO PROJETO
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(0, 10, "Detalhes do Projeto")
    pdf.ln(12)
    
    specs = [
        ("Produto", dados.get("produto", "Cartao de visita premium")),
        ("Formato", dados.get("formato", "5x9 cm (tradicional)")),
        ("Material", dados.get("material", "A definir")),
        ("Acabamento(s)", dados.get("acabamento", "A definir")),
        ("Quantidade", dados.get("quantidade", "A definir")),
        ("Arte/Criacao", dados.get("criacao", dados.get("arte", "A definir"))),
        ("Area de atuacao", dados.get("area", "A definir")),
    ]
    
    pdf.set_font("Helvetica", "", 11)
    for label, valor in specs:
        pdf.set_text_color(120, 120, 120)
        pdf.cell(60, 8, label)
        pdf.set_text_color(26, 26, 26)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, str(valor))
        pdf.ln(8)
        pdf.set_font("Helvetica", "", 11)
    
    if dados.get("urgencia"):
        pdf.ln(5)
        pdf.set_text_color(180, 50, 50)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, f"Urgencia: {dados.get('urgencia')}")
        pdf.set_text_color(60, 60, 60)
    
    # INVESTIMENTO
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(0, 10, "Investimento")
    pdf.ln(12)
    
    media = dados.get("media", 0)
    valor_criacao = dados.get("valor_criacao", 0)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    
    pdf.cell(120, 8, "Producao do material (base)")
    pdf.set_font("Helvetica", "B", 11)
    if valor_criacao:
        pdf.cell(0, 8, f"R$ {(media - valor_criacao):,.2f}", align="R")
    else:
        pdf.cell(0, 8, f"R$ {media:,.2f}", align="R")
    pdf.ln(8)
    
    pdf.set_font("Helvetica", "", 11)
    if valor_criacao:
        tipo_criacao = dados.get("criacao", "Criacao de arte")
        pdf.cell(120, 8, tipo_criacao.replace("_", " ").title())
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, f"R$ {valor_criacao:,.2f}", align="R")
        pdf.ln(8)
    
    pdf.ln(5)
    pdf.set_draw_color(180, 150, 50)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(120, 10, "INVESTIMENTO ESTIMADO")
    pdf.set_text_color(180, 150, 50)
    pdf.cell(0, 10, f"R$ {media:,.2f}", align="R")
    pdf.ln(15)
    
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 5, (
        "* Valores estimados com base nas especificacoes informadas. "
        "O orcamento final e personalizado conforme acabamentos, "
        "criacao e complexidade do projeto.\n"
        f"* Proposta valida ate {validade}.\n"
        "* Condicoes de pagamento: PIX, cartao ou boleto."
    ))
    
    # PRÓXIMOS PASSOS
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(0, 10, "Proximos Passos")
    pdf.ln(12)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    
    passos = [
        "1. Aprovacao da proposta (responda este e-mail ou fale conosco pelo WhatsApp)",
        "2. Envio ou aprovacao da arte final",
        "3. Confirmacao do pagamento",
        "4. Inicio da producao (prazo medio: 5 a 8 dias uteis)",
        "5. Controle de qualidade e finalizacao",
        "6. Envio ou retirada do material"
    ]
    
    for passo in passos:
        pdf.cell(0, 8, passo)
        pdf.ln(8)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(0, 8, "Contato direto:")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, "E-mail: ola@primyn.com")
    pdf.ln(6)
    pdf.cell(0, 8, "Instagram: @primyn.store")
    pdf.ln(6)
    pdf.cell(0, 8, "Site: primyn.com")
    
    # SALVAR
    os.makedirs("propostas", exist_ok=True)
    nome_arquivo = f"proposta_{nome.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    caminho = os.path.join("propostas", nome_arquivo)
    
    pdf.output(caminho)
    print(f"[PDF] Proposta gerada: {caminho}")
    
    return caminho

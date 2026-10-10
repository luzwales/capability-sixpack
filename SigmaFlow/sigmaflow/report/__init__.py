"""
sigmaflow/report/
==================
Sistema de geracao de relatorios Markdown/PDF academicos (padrao DMAIC).

Arquitetura:
  markdown_report.py     -- motor principal, gera relatorios Markdown
  latex_engine.py        -- motor LaTeX legado (para conversao PDF via pandoc)
  section_builder.py     -- constroi contextos Jinja2 por secao
  interpretation_engine.py -- gera interpretacoes textuais automaticas
  template_renderer.py   -- renderiza templates Jinja2 para .tex

Uso rapido:
    from sigmaflow.report import MarkdownReportGenerator

    md = MarkdownReportGenerator(
        results       = engine_results,
        output_dir    = "output/reports",
        title         = "SigmaFlow Analysis Report",
    ).generate()
"""
from .markdown_report       import MarkdownReportGenerator
from .latex_engine          import LatexEngine
from .interpretation_engine import InterpretationEngine
from .section_builder       import SectionBuilder
from .template_renderer     import TemplateRenderer

__all__ = [
    "MarkdownReportGenerator",
    "LatexEngine",
    "InterpretationEngine",
    "SectionBuilder",
    "TemplateRenderer",
]

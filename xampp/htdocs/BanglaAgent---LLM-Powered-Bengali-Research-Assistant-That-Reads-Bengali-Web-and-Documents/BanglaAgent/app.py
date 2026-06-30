import os
import logging
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

from src.agent import BanglaAgent
from src.utils.ui_helpers import (
    format_sources_html,
    format_evidence_html,
    format_error_message,
    PROGRESS_MESSAGES,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

agent = BanglaAgent()

CUSTOM_CSS = """
/* Global */
.gradio-container {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%) !important;
    font-family: 'Segoe UI', 'Noto Sans Bengali', system-ui, sans-serif !important;
    min-height: 100vh;
}

/* Header */
.header-section {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
    border: 1px solid #334155;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    text-align: center;
}
.header-section h1 {
    color: #f8fafc !important;
    font-size: 2.2em !important;
    font-weight: 700 !important;
    margin: 0 0 4px 0 !important;
    letter-spacing: -0.5px;
}
.header-section .tagline {
    color: #94a3b8;
    font-size: 1.05em;
    margin-top: 4px;
}
.badge {
    display: inline-block;
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: #0f172a;
    font-size: 0.75em;
    font-weight: 700;
    padding: 3px 12px;
    border-radius: 20px;
    margin-top: 8px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* Cards */
.card-panel {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2) !important;
}

/* Sidebar */
.sidebar-section {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px;
}
.sidebar-section label, .sidebar-section .label-wrap span {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
}

/* Inputs */
.gradio-container input[type="text"],
.gradio-container textarea {
    background: #0f172a !important;
    border: 1px solid #475569 !important;
    color: #f8fafc !important;
    border-radius: 8px !important;
}
.gradio-container input[type="text"]:focus,
.gradio-container textarea:focus {
    border-color: #f59e0b !important;
    box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2) !important;
}

/* Buttons */
.primary-btn {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 1.05em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    box-shadow: 0 4px 12px rgba(245,158,11,0.3) !important;
    transition: all 0.2s ease !important;
}
.primary-btn:hover {
    box-shadow: 0 6px 20px rgba(245,158,11,0.5) !important;
    transform: translateY(-1px) !important;
}
.secondary-btn {
    background: #334155 !important;
    color: #e2e8f0 !important;
    border: 1px solid #475569 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
.secondary-btn:hover {
    background: #475569 !important;
}

/* Example buttons */
.example-btn {
    background: #1e293b !important;
    color: #cbd5e1 !important;
    border: 1px solid #475569 !important;
    border-radius: 8px !important;
    font-size: 0.9em !important;
    padding: 8px 14px !important;
    transition: all 0.2s ease !important;
}
.example-btn:hover {
    border-color: #f59e0b !important;
    color: #f59e0b !important;
}

/* Output panels */
.answer-panel {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    color: #e2e8f0;
    line-height: 1.7;
}
.answer-panel h2 {
    color: #f59e0b !important;
    font-size: 1.15em !important;
    margin-top: 16px !important;
}
.answer-panel ul, .answer-panel ol {
    padding-left: 20px;
}

/* Status */
.status-indicator {
    background: #1e293b;
    border-left: 3px solid #f59e0b;
    color: #94a3b8;
    padding: 8px 14px;
    border-radius: 0 8px 8px 0;
    font-size: 0.9em;
    margin-bottom: 12px;
}

/* Dropdown, slider, checkbox */
.gradio-container .gr-dropdown,
.gradio-container select {
    background: #0f172a !important;
    color: #f8fafc !important;
    border: 1px solid #475569 !important;
    border-radius: 8px !important;
}
.gradio-container .gr-checkbox label {
    color: #cbd5e1 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #64748b; }

/* Accordion */
.gradio-container .gr-accordion {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}

/* Tabs */
.gradio-container .tab-nav button {
    color: #94a3b8 !important;
    border: none !important;
    background: transparent !important;
}
.gradio-container .tab-nav button.selected {
    color: #f59e0b !important;
    border-bottom: 2px solid #f59e0b !important;
}

/* File upload */
.gradio-container .file-upload {
    background: #0f172a !important;
    border: 2px dashed #475569 !important;
    border-radius: 10px !important;
}

/* Markdown output */
.gradio-container .markdown-text {
    color: #e2e8f0 !important;
}

/* Footer */
.footer-section {
    text-align: center;
    color: #64748b;
    font-size: 0.85em;
    margin-top: 16px;
    padding: 12px;
}
"""

HEADER_HTML = """
<div class="header-section">
    <h1>BanglaAgent</h1>
    <p class="tagline">Bengali Research Assistant for Web, PDFs, and Source-backed Answers</p>
    <span class="badge">Agentic AI</span>
    <p style="color:#64748b; font-size:0.88em; margin-top:10px;">
        বাংলা ওয়েব সোর্স অনুসন্ধান | PDF বিশ্লেষণ | সূত্রসহ উত্তর | পডকাস্ট স্ক্রিপ্ট
    </p>
</div>
"""


def run_agent(
    question: str,
    pdf_file,
    use_web: bool,
    use_pdf: bool,
    mode: str,
    top_k: int,
    answer_language: str,
    include_podcast: bool,
    progress=gr.Progress(),
):
    logger.info("[UI] Run clicked")
    logger.info(f"[UI] question={question!r}")
    logger.info(f"[UI] pdf_file={pdf_file}")
    logger.info(f"[UI] use_web={use_web}, use_pdf={use_pdf}")
    logger.info(f"[UI] mode={mode}, top_k={top_k}")
    logger.info(f"[UI] answer_language={answer_language}, podcast={include_podcast}")

    if not question or not question.strip():
        return (
            "অনুগ্রহ করে একটি প্রশ্ন লিখুন।",
            "",
            "",
            "",
        )

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-your"):
        return (
            format_error_message(
                "OPENAI_API_KEY সেট করা নেই। .env ফাইলে আপনার API key যোগ করুন।"
            ),
            "",
            "",
            "",
        )

    try:
        pdf_path = None
        if pdf_file is not None and use_pdf:
            progress(0.1, desc=PROGRESS_MESSAGES["pdf_reading"])
            if hasattr(pdf_file, "name"):
                pdf_path = pdf_file.name
            else:
                pdf_path = str(pdf_file)

        if use_web:
            progress(0.3, desc=PROGRESS_MESSAGES["web_searching"])

        progress(0.5, desc=PROGRESS_MESSAGES["retrieving"])

        effective_mode = mode
        if include_podcast and mode != "Podcast Script":
            effective_mode = "Podcast Script"

        progress(0.7, desc=PROGRESS_MESSAGES["generating"])

        result = agent.run(
            question=question,
            pdf_file=pdf_path,
            use_web=use_web,
            use_pdf=use_pdf,
            mode=effective_mode,
            top_k=int(top_k),
            answer_language=answer_language,
            podcast_format=include_podcast,
        )

        progress(1.0, desc="সম্পন্ন!")

        answer = result.get("answer", "")
        evidence = result.get("evidence", [])
        limitations = result.get("limitations", "")

        citations_html = format_sources_html(evidence)
        evidence_html = format_evidence_html(evidence)

        limitations_text = ""
        if limitations:
            limitations_text = f"### সীমাবদ্ধতা\n{limitations}"

        return answer, citations_html, evidence_html, limitations_text

    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
        return (
            format_error_message(f"একটি ত্রুটি ঘটেছে: {str(e)}"),
            "",
            "",
            "",
        )


def clear_session():
    logger.info("[UI] Clear session clicked")
    agent.clear_session()
    return (
        "",              # question_input
        None,            # pdf_upload
        "",              # answer_output
        "",              # citations_output
        "",              # evidence_output
        "",              # limitations_output
        "Detailed Research Answer",  # mode_dropdown
        True,            # use_web_checkbox
        False,           # use_pdf_checkbox
        False,           # include_podcast_checkbox
        5,               # top_k_slider
        "Bengali",       # language_dropdown
    )


def set_example(example_text: str):
    return example_text


def build_ui():
    with gr.Blocks(
        css=CUSTOM_CSS,
        title="BanglaAgent — Bengali Research Assistant",
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.amber,
            secondary_hue=gr.themes.colors.slate,
            neutral_hue=gr.themes.colors.slate,
        ),
    ) as demo:
        gr.HTML(HEADER_HTML)

        with gr.Row():
            # --- Left Sidebar ---
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### Settings", elem_classes=["sidebar-section"])

                pdf_upload = gr.File(
                    label="PDF আপলোড করুন",
                    file_types=[".pdf"],
                    type="filepath",
                    interactive=True,
                )

                mode_dropdown = gr.Dropdown(
                    label="আউটপুট মোড",
                    choices=[
                        "Detailed Research Answer",
                        "Quick Summary",
                        "Podcast Script",
                    ],
                    value="Detailed Research Answer",
                    interactive=True,
                )

                use_web_checkbox = gr.Checkbox(
                    label="বাংলা ওয়েব সার্চ",
                    value=True,
                    interactive=True,
                )
                use_pdf_checkbox = gr.Checkbox(
                    label="আপলোডেড PDF ব্যবহার",
                    value=False,
                    interactive=True,
                )
                include_podcast_checkbox = gr.Checkbox(
                    label="পডকাস্ট ফরম্যাট",
                    value=False,
                    interactive=True,
                )

                with gr.Accordion("Retrieval Settings", open=False):
                    top_k_slider = gr.Slider(
                        minimum=1,
                        maximum=15,
                        value=5,
                        step=1,
                        label="Top-K ফলাফল",
                        interactive=True,
                    )
                    language_dropdown = gr.Dropdown(
                        label="উত্তরের ভাষা",
                        choices=["Bengali", "English", "Mixed"],
                        value="Bengali",
                        interactive=True,
                    )

                clear_btn = gr.Button(
                    "সেশন ক্লিয়ার করুন",
                    elem_classes=["secondary-btn"],
                )

            # --- Right Main Panel ---
            with gr.Column(scale=3):
                question_input = gr.Textbox(
                    label="আপনার প্রশ্ন লিখুন",
                    placeholder="যেমন: বাংলাদেশ বাজেট সহজ ভাষায় ব্যাখ্যা করো...",
                    lines=3,
                    max_lines=6,
                )

                run_btn = gr.Button(
                    "অনুসন্ধান শুরু করুন",
                    elem_classes=["primary-btn"],
                    size="lg",
                )

                gr.Markdown("**উদাহরণ প্রশ্ন:**")
                with gr.Row():
                    ex1 = gr.Button(
                        "বাংলাদেশ বাজেট সহজ ভাষায় ব্যাখ্যা করো",
                        elem_classes=["example-btn"],
                        size="sm",
                    )
                    ex2 = gr.Button(
                        "এই PDF থেকে মূল পয়েন্টগুলো বের করো",
                        elem_classes=["example-btn"],
                        size="sm",
                    )
                with gr.Row():
                    ex3 = gr.Button(
                        "এই বিষয়ে একটি বাংলা পডকাস্ট স্ক্রিপ্ট বানাও",
                        elem_classes=["example-btn"],
                        size="sm",
                    )
                    ex4 = gr.Button(
                        "Prothom Alo ও Daily Star থেকে সাম্প্রতিক তথ্য দাও",
                        elem_classes=["example-btn"],
                        size="sm",
                    )

                # Output tabs
                with gr.Tabs():
                    with gr.TabItem("উত্তর"):
                        answer_output = gr.Markdown(
                            label="উত্তর",
                            elem_classes=["answer-panel"],
                        )

                    with gr.TabItem("সূত্র"):
                        citations_output = gr.HTML(label="সূত্র")

                    with gr.TabItem("প্রমাণ"):
                        evidence_output = gr.HTML(label="ব্যবহৃত প্রমাণ")

                    with gr.TabItem("সীমাবদ্ধতা"):
                        limitations_output = gr.Markdown(label="সীমাবদ্ধতা")

        # Footer
        gr.HTML("""
        <div class="footer-section">
            <p>BanglaAgent — Agentic AI Research Assistant for Bengali</p>
            <p>Built with OpenAI | LangChain | FAISS | Gradio</p>
        </div>
        """)

        # --- Event Handlers ---
        run_inputs = [
            question_input,
            pdf_upload,
            use_web_checkbox,
            use_pdf_checkbox,
            mode_dropdown,
            top_k_slider,
            language_dropdown,
            include_podcast_checkbox,
        ]
        run_outputs = [
            answer_output,
            citations_output,
            evidence_output,
            limitations_output,
        ]

        run_btn.click(
            fn=run_agent,
            inputs=run_inputs,
            outputs=run_outputs,
        )

        question_input.submit(
            fn=run_agent,
            inputs=run_inputs,
            outputs=run_outputs,
        )

        clear_btn.click(
            fn=clear_session,
            inputs=[],
            outputs=[
                question_input,
                pdf_upload,
                answer_output,
                citations_output,
                evidence_output,
                limitations_output,
                mode_dropdown,
                use_web_checkbox,
                use_pdf_checkbox,
                include_podcast_checkbox,
                top_k_slider,
                language_dropdown,
            ],
        )

        ex1.click(fn=lambda: "বাংলাদেশ বাজেট সহজ ভাষায় ব্যাখ্যা করো", outputs=question_input)
        ex2.click(fn=lambda: "এই PDF থেকে মূল পয়েন্টগুলো বের করো", outputs=question_input)
        ex3.click(fn=lambda: "এই বিষয়ে একটি বাংলা পডকাস্ট স্ক্রিপ্ট বানাও", outputs=question_input)
        ex4.click(fn=lambda: "Prothom Alo ও Daily Star থেকে সাম্প্রতিক তথ্য দাও", outputs=question_input)

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import is_pdf_specific_query, is_web_explicit_query


def test_pdf_specific_bengali():
    assert is_pdf_specific_query("এই PDF অনুযায়ী বাজেটের প্রধান অগ্রাধিকার কী?")
    assert is_pdf_specific_query("এই ডকুমেন্ট থেকে তথ্য দাও")
    assert is_pdf_specific_query("PDF থেকে মূল পয়েন্ট বের করো")
    assert is_pdf_specific_query("আপলোড করা PDF এর সারসংক্ষেপ দাও")
    assert is_pdf_specific_query("এই রিপোর্ট অনুযায়ী কী হয়েছে?")


def test_pdf_specific_english():
    assert is_pdf_specific_query("What does this PDF say about budget?")
    assert is_pdf_specific_query("from this PDF, extract the key points")
    assert is_pdf_specific_query("according to the PDF, what is the main topic?")
    assert is_pdf_specific_query("uploaded PDF summary")


def test_not_pdf_specific():
    assert not is_pdf_specific_query("বাংলাদেশ বাজেট ব্যাখ্যা করো")
    assert not is_pdf_specific_query("Prothom Alo থেকে সাম্প্রতিক তথ্য দাও")
    assert not is_pdf_specific_query("What is the GDP of Bangladesh?")


def test_web_explicit():
    assert is_web_explicit_query("ওয়েব থেকে সাম্প্রতিক তথ্য দাও")
    assert is_web_explicit_query("latest news about Bangladesh")
    assert is_web_explicit_query("এই PDF এর সাথে তুলনা করো")
    assert is_web_explicit_query("web search for budget info")


def test_not_web_explicit():
    assert not is_web_explicit_query("এই PDF অনুযায়ী বাজেটের তথ্য দাও")
    assert not is_web_explicit_query("মূল পয়েন্ট বের করো")


def test_pdf_specific_with_web_explicit():
    q = "এই PDF-এর তথ্যের সাথে সাম্প্রতিক ওয়েব তথ্য তুলনা করো"
    assert is_pdf_specific_query(q)
    assert is_web_explicit_query(q)

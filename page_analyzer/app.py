import os

import requests
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from page_analyzer.parser import parse_content
from page_analyzer.db import url_repo
from page_analyzer.validators import normalize_url, validate

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/urls")
def urls():
    all_urls = url_repo.get_all_urls()
    last_checks = url_repo.get_all_last_checks()

    urls_with_checks = []
    for url in all_urls:
        last_check = last_checks.get(url.id)
        urls_with_checks.append((url, last_check))

    return render_template("urls.html", urls_with_checks=urls_with_checks)


@app.get("/urls/<int:id>")
def show_url(id):
    url = url_repo.get_url_by_id(id)
    if not url:
        flash("Страница не найдена", "danger")
        return redirect(url_for("index"))
    checks = url_repo.get_checks_for_url(id)
    return render_template("url.html", url=url, checks=checks)


@app.post("/urls")
def add_url():
    raw_url = request.form.get("url")
    if not validate(raw_url):
        return render_template("index.html", url=raw_url), 422

    normalized_url = normalize_url(raw_url)

    existing_url = url_repo.get_url_by_name(normalized_url)
    if existing_url:
        flash("Страница уже существует", "info")
        return redirect(url_for("show_url", id=existing_url.id))

    url_id = url_repo.add_url(normalized_url)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("show_url", id=url_id))


@app.post("/urls/<int:url_id>/checks")
def add_check(url_id):
    url = url_repo.get_url_by_id(url_id)
    try:
        response = requests.get(url.name, timeout=5)
        response.raise_for_status()
        status_code = response.status_code
        html_values = parse_content(response.text)
        url_repo.add_url_check(url_id, status_code, html_values)

        flash("Страница успешно проверена", "success")
    except requests.exceptions.RequestException:
        flash("Произошла ошибка при проверке", "danger")
    except Exception as e:
        flash(f"Ошибка: {str(e)}", "danger")

    return redirect(url_for("show_url", id=url_id))

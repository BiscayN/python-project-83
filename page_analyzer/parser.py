from bs4 import BeautifulSoup


def parse_content(content):
    soup = BeautifulSoup(content, "html.parser")

    h1_tag = soup.find("h1")
    h1 = h1_tag.text.strip() if h1_tag else ""

    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else ""

    meta_desc = soup.find("meta", attrs={"name": "description"})
    description = meta_desc.get(
        "content", "").strip() if meta_desc and meta_desc.get(
        "content") else ""

    return {
        "h1": h1,
        "title": title,
        "description": description
    }

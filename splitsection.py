from pemx import pmab, epub

path = r"E:\books\raw\尘缘.pmab"

start = 0
sections = [
    ("卷一 无名", 49),
    ("卷二 逐鹿", 18),
    ("卷三 碧落黄泉", 17),
    ("卷四 忽闻海外有仙山", 5),
    ]

print("chapter count:", sum(x[1] for x in sections))

book = pmab.parse(open(path, "rb"))
for title, count in sections:
    section = pmab.PMABSection(title=title)
    section.extend(range(start, start + count))
    start += count
    for i in section:
        chapter = book[i]
        chapter.title = chapter.title.strip()
        chapter.title = chapter.title.replace(title, "").lstrip()

    book.sections.append(section)

out = "r"
pmab.make(book, out)

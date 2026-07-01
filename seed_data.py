import sqlite3

reading_paths = [
    {
        "author": "Mitch Albom",
        "books": [
            (1, "Tuesdays with Morrie", "A deeply moving account of life's most important lessons, told through the bond between a student and his dying professor. Albom's writing is warm, accessible, and immediately engaging — the perfect introduction to his voice before exploring the rest of his work."),
            (2, "For One More Day", "Once you've experienced Albom's emotional depth in Tuesdays with Morrie, this novel about second chances and family will resonate even more deeply.")
        ]
    },
    {
        "author": "Paulo Coelho",
        "books": [
            (1, "The Alchemist", "Coelho's most celebrated work and the ideal starting point. A timeless fable about following your dreams, it introduces his signature philosophical storytelling in its most distilled and accessible form. Every subsequent Coelho book makes more sense after this one."),
        ]
    },
    {
        "author": "Khaled Hosseini",
        "books": [
            (1, "The Kite Runner", "Hosseini's debut novel is his most straightforward in narrative structure, making it the ideal entry point. It draws you into his world of Afghanistan with urgency and emotional power before you take on the even more layered A Thousand Splendid Suns."),
            (2, "A Thousand Splendid Suns", "After The Kite Runner prepares you for Hosseini's emotional intensity, this novel about the resilience of Afghan women will hit you with a force you won't forget.")
        ]
    },
    {
        "author": "Charlotte Bronte",
        "books": [
            (1, "Jane Eyre", "Brontë's masterpiece and her most complete work. The story of Jane's quiet strength and independence feels remarkably modern despite being written in 1847. There is no debate about where to begin with Brontë — this is it.")
        ]
    },
    {
        "author": "Mieko Kawakami",
        "books": [
            (1, "All the Lovers in the Night", "A quieter, more introspective entry point into Kawakami's world. Its restrained prose and intimate portrayal of loneliness make it far more accessible than her celebrated but demanding Breasts and Eggs. Start here to understand her voice before going deeper."),
            (2, "Breasts and Eggs", "Once you're comfortable with Kawakami's style, this ambitious novel about womanhood and identity in modern Japan will reward you fully.")
        ]
    },
    {
        "author": "George Orwell",
        "books": [
            (1, "Animal Farm", "At under 100 pages, this razor-sharp political allegory is the perfect first Orwell. It introduces his themes of power, corruption, and propaganda in their most digestible form. Do not start with 1984 — let Animal Farm prepare your mind first."),
            (2, "1984", "After Animal Farm lays the groundwork, Orwell's dystopian masterpiece will land with its full intended weight. One of the most important novels ever written — but best experienced after you know what Orwell is doing.")
        ]
    },
    {
        "author": "Alexandre Dumas",
        "books": [
            (1, "The Count of Monte Cristo", "Dumas' greatest work and one of the finest adventure novels ever written. A sweeping tale of betrayal, imprisonment, and meticulous revenge that remains gripping across every one of its pages. There is no better place to begin with Dumas — or perhaps with literature itself.")
        ]
    },
    {
        "author": "Dolly Alderton",
        "books": [
            (1, "Everything I Know About Love", "Alderton's debut memoir is her most personal and most universally loved work. A brilliantly honest account of female friendship, heartbreak, and growing up, written with warmth and razor-sharp wit. Start here — it will make you feel seen in ways you didn't expect.")
        ]
    }
]

conn = sqlite3.connect("books.db")
cursor = conn.cursor()

for author_data in reading_paths:
    author = author_data["author"]
    for book in author_data["books"]:
        order_num, book_title, why = book
        cursor.execute(
            "INSERT INTO reading_paths (author, book_title, order_num, why_start_here) VALUES (?, ?, ?, ?)",
            (author, book_title, order_num, why)
        )
        print(f"✅ Added '{book_title}' by {author}")

conn.commit()
conn.close()
print("\n🎉 All reading paths added successfully!")
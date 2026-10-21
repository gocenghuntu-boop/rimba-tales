"""Local story engine for Rimba Tales.

A small, fully offline story composer. It assembles a calming bedtime
story from hand-written scenes: one animal hero, one gentle problem tied
to a theme, one kind action, one lesson, and a sleepy closing ritual.

It needs no API key, no network, and no model download, so the app can
always tell a story. When GROQ_API_KEY is configured, app.py prefers a
live open-weight model (Llama) and uses this engine as the fallback.
"""

ANIMALS = {
    "elephant": {
        "en": {
            "name": "Nara the Elephant",
            "short": "Nara",
            "home": "the bamboo grove by the river",
            "gift": "she remembered every path in the forest and could carry anything on her broad back",
        },
        "id": {
            "name": "Nara si Gajah",
            "short": "Nara",
            "home": "rumpun bambu di tepi sungai",
            "gift": "ia ingat semua jalan di hutan dan bisa membawa apa saja di punggungnya yang lebar",
        },
    },
    "lion": {
        "en": {
            "name": "Raka the Lion Cub",
            "short": "Raka",
            "home": "the warm grass hill above the valley",
            "gift": "his roar was still small, but his heart was the bravest on the hill",
        },
        "id": {
            "name": "Raka si Anak Singa",
            "short": "Raka",
            "home": "bukit rumput hangat di atas lembah",
            "gift": "aumannya masih kecil, tapi hatinya yang paling berani di bukit itu",
        },
    },
    "owl": {
        "en": {
            "name": "Luma the Owl",
            "short": "Luma",
            "home": "the big old banyan tree",
            "gift": "she could see kindly in the dark and loved answering questions slowly, one by one",
        },
        "id": {
            "name": "Luma si Burung Hantu",
            "short": "Luma",
            "home": "pohon beringin tua yang besar",
            "gift": "ia bisa melihat dengan baik di kegelapan dan suka menjawab pertanyaan pelan-pelan, satu per satu",
        },
    },
    "mousedeer": {
        "en": {
            "name": "Kiki the Mousedeer",
            "short": "Kiki",
            "home": "the fern patch under the rain tree",
            "gift": "he was the smallest in the forest, and the quickest thinker of them all",
        },
        "id": {
            "name": "Kiki si Kancil",
            "short": "Kiki",
            "home": "semak pakis di bawah pohon hujan",
            "gift": "ia yang paling kecil di hutan, dan yang paling cepat berpikir di antara semuanya",
        },
    },
    "turtle": {
        "en": {
            "name": "Sasa the Turtle",
            "short": "Sasa",
            "home": "the quiet pond behind the waterfall",
            "gift": "she never hurried, and somehow she always arrived exactly when she was needed",
        },
        "id": {
            "name": "Sasa si Kura-Kura",
            "short": "Sasa",
            "home": "kolam tenang di belakang air terjun",
            "gift": "ia tidak pernah terburu-buru, dan entah bagaimana ia selalu tiba tepat saat dibutuhkan",
        },
    },
}

THEMES = {
    "kindness": {
        "en": {
            "label": "Kindness",
            "scene": (
                "Just then, {short} heard a tiny voice near the roots. It was Pip, a little firefly, "
                "sitting all alone. Pip's light had gone dim with worry, because the other fireflies "
                "had flown home and the path through the dark trees looked so big and so scary."
            ),
            "action": (
                "{short} did not say, hurry up. {short} did not say, it is nothing. Instead, {short} "
                "sat down in the soft grass and stayed. Together they watched the first stars. "
                "Slowly, slowly, Pip's breathing calmed, and a warm little glow came back, one blink at a time."
            ),
            "lesson": "\"Kindness does not have to be big,\" whispered the moon. \"Sometimes kindness is simply staying, so nobody has to be afraid alone.\"",
        },
        "id": {
            "label": "Kebaikan Hati",
            "scene": (
                "Tiba-tiba, {short} mendengar suara kecil di dekat akar pohon. Itu Pip, kunang-kunang kecil, "
                "yang duduk sendirian. Cahaya Pip meredup karena khawatir, karena kunang-kunang lain sudah pulang "
                "dan jalan melewati pohon-pohon gelap terlihat begitu besar dan menakutkan."
            ),
            "action": (
                "{short} tidak berkata, ayo cepat. {short} juga tidak berkata, ah itu bukan apa-apa. Sebaliknya, {short} "
                "duduk di rumput yang lembut dan menemani. Bersama mereka memandangi bintang-bintang pertama. "
                "Pelan-pelan, napas Pip menjadi tenang, dan cahaya kecil yang hangat kembali menyala, satu kedip demi satu kedip."
            ),
            "lesson": "\"Kebaikan hati tidak harus besar,\" bisik sang bulan. \"Kadang kebaikan hati cukup dengan menemani, supaya tidak ada yang takut sendirian.\"",
        },
    },
    "courage": {
        "en": {
            "label": "Courage",
            "scene": (
                "Just then, a soft whimper floated down from the bushes. Beni, a baby hornbill, had tumbled "
                "from his nest onto a bed of leaves. He was not hurt, but the nest was high, the night was "
                "coming, and Beni was too frightened to call out loudly."
            ),
            "action": (
                "{short} felt a little afraid too, and that is all right. Bravery is not having no fear. "
                "Bravery is taking one small step while your knees still shake. So {short} took one step, "
                "then another, and called gently until Beni's mother heard and swooped down with open wings."
            ),
            "lesson": "\"Being brave,\" said the moon, \"means your feet move even when your heart is thumping. One small step is enough to begin.\"",
        },
        "id": {
            "label": "Keberanian",
            "scene": (
                "Tiba-tiba, terdengar rengekan lembut dari semak-semak. Beni, bayi burung enggang, terjatuh "
                "dari sarangnya ke atas tumpukan daun. Ia tidak terluka, tapi sarangnya tinggi, malam mulai turun, "
                "dan Beni terlalu takut untuk berteriak keras."
            ),
            "action": (
                "{short} juga merasa sedikit takut, dan itu tidak apa-apa. Berani bukan berarti tidak punya rasa takut. "
                "Berani artinya melangkah satu langkah kecil selagi lututmu masih gemetar. Jadi {short} melangkah satu kali, "
                "lalu satu kali lagi, dan memanggil dengan lembut sampai ibu Beni mendengar dan terbang turun dengan sayap terbuka."
            ),
            "lesson": "\"Berani,\" kata sang bulan, \"artinya kakimu tetap melangkah walaupun jantungmu berdebar. Satu langkah kecil sudah cukup untuk memulai.\"",
        },
    },
    "friendship": {
        "en": {
            "label": "Friendship",
            "scene": (
                "Just then, {short} spotted Tobi, a young monkey, sitting on a low branch with his tail curled "
                "tight. Tobi had quarrelled with his best friend that morning over the last mango, and now the "
                "forest felt lonely, even with a hundred sounds around him."
            ),
            "action": (
                "{short} climbed up slowly and sat nearby, not too close. They shared the quiet for a while. "
                "Then {short} said, a mango is sweet for one minute, but a friend is sweet for a whole life. "
                "Tobi smiled for the first time that evening, and decided to find his friend at sunrise and say sorry first."
            ),
            "lesson": "\"A friend,\" smiled the moon, \"is someone who makes the forest feel small when you are sad, and big when you play together.\"",
        },
        "id": {
            "label": "Persahabatan",
            "scene": (
                "Tiba-tiba, {short} melihat Tobi, monyet muda, duduk di dahan rendah dengan ekor melingkar rapat. "
                "Tobi bertengkar dengan sahabatnya pagi itu gara-gara mangga terakhir, dan sekarang hutan terasa sepi, "
                "walaupun ada seratus bunyi di sekelilingnya."
            ),
            "action": (
                "{short} naik perlahan dan duduk di dekatnya, tidak terlalu dekat. Mereka berbagi keheningan sebentar. "
                "Lalu {short} berkata, mangga manisnya cuma semenit, tapi sahabat manisnya seumur hidup. "
                "Tobi tersenyum untuk pertama kalinya malam itu, dan berjanji mencari sahabatnya saat matahari terbit dan meminta maaf lebih dulu."
            ),
            "lesson": "\"Sahabat,\" senyum sang bulan, \"adalah seseorang yang membuat hutan terasa kecil saat kamu sedih, dan terasa besar saat kalian bermain bersama.\"",
        },
    },
    "gratitude": {
        "en": {
            "label": "Gratitude",
            "scene": (
                "Just then, the rain began to tap, tap, tap on the leaves. It was only a drizzle, but the dry "
                "little pond near {short}'s home sighed with relief. All week the pond had waited, cracked and "
                "thirsty, while everyone walked past too busy to notice."
            ),
            "action": (
                "{short} stopped and watched the rings grow on the water. Then {short} did something simple: "
                "{short} said thank you. Thank you to the rain, thank you to the pond, thank you to the tree "
                "that gave shade every hot afternoon. And somehow, saying it out loud made the whole evening feel warmer."
            ),
            "lesson": "\"Gratitude,\" hummed the moon, \"is noticing the good things before they are gone, and saying their names out loud.\"",
        },
        "id": {
            "label": "Rasa Syukur",
            "scene": (
                "Tiba-tiba, hujan mulai mengetuk, tuk, tuk, tuk di dedaunan. Memang hanya gerimis, tapi kolam kecil "
                "yang kering di dekat rumah {short} menghela napas lega. Seminggu penuh kolam itu menunggu, retak dan "
                "kehausan, sementara semua orang lewat terlalu sibuk untuk memperhatikan."
            ),
            "action": (
                "{short} berhenti dan memandangi lingkaran-lingkaran yang membesar di air. Lalu {short} melakukan hal sederhana: "
                "{short} mengucapkan terima kasih. Terima kasih untuk hujan, terima kasih untuk kolam, terima kasih untuk pohon "
                "yang memberi keteduhan setiap siang yang panas. Dan entah bagaimana, mengucapkannya dengan suara membuat malam itu terasa lebih hangat."
            ),
            "lesson": "\"Rasa syukur,\" senandung sang bulan, \"adalah menyadari hal-hal baik sebelum mereka pergi, dan menyebut namanya dengan suara.\"",
        },
    },
    "patience": {
        "en": {
            "label": "Patience",
            "scene": (
                "Just then, {short} noticed a small green sprout pushing through the soil. It had been planted "
                "many days ago, and every morning a little squirrel came to stare at it, sighing, why are you "
                "not a tree yet? Tonight the squirrel was sighing again, louder than the crickets."
            ),
            "action": (
                "{short} lay down beside the sprout and the squirrel, and they simply waited together. They "
                "listened to the night. They counted fireflies. And {short} said, growing is quiet work. "
                "The sprout was not lazy. It was busy underground, where nobody could see."
            ),
            "lesson": "\"Patience,\" said the moon, \"is trusting that good things are growing, even on the days you cannot see them yet.\"",
        },
        "id": {
            "label": "Kesabaran",
            "scene": (
                "Tiba-tiba, {short} memperhatikan tunas hijau kecil yang menerobos tanah. Tunas itu ditanam "
                "berhari-hari yang lalu, dan setiap pagi seekor tupai kecil datang menatapnya sambil menghela napas, "
                "kenapa kamu belum jadi pohon? Malam ini tupai itu menghela napas lagi, lebih keras dari bunyi jangkrik."
            ),
            "action": (
                "{short} berbaring di samping tunas dan tupai itu, dan mereka menunggu bersama. Mereka "
                "mendengarkan malam. Mereka menghitung kunang-kunang. Dan {short} berkata, bertumbuh itu pekerjaan yang sunyi. "
                "Tunas itu tidak malas. Ia sedang sibuk di bawah tanah, di tempat yang tidak bisa dilihat siapa pun."
            ),
            "lesson": "\"Kesabaran,\" kata sang bulan, \"adalah percaya bahwa hal-hal baik sedang bertumbuh, bahkan di hari-hari saat kamu belum bisa melihatnya.\"",
        },
    },
}

OPENING = {
    "en": (
        "In the Rimba forest, when the sun slides behind the hills and the sky turns the colour of "
        "warm honey, all the animals slow down. Deep in {home} lived {name}. {cap_gift}. "
        "Tonight, {short} had brushed the dust of the day away, fluffed up a bed of soft leaves, "
        "and was just about to close two sleepy eyes."
    ),
    "id": (
        "Di hutan Rimba, saat matahari meluncur ke balik bukit dan langit berubah warna seperti "
        "madu hangat, semua hewan bergerak lebih pelan. Jauh di {home} tinggalah {name}. "
        "{cap_gift}. Malam ini, {short} sudah membersihkan debu hari ini, menepuk-nepuk kasur daunnya "
        "yang lembut, dan baru saja hendak memejamkan dua matanya yang mengantuk."
    ),
}

CLOSING = {
    "en": (
        "One by one, the lights of the forest went out. The crickets played their quiet song. "
        "{short} curled up in the soft leaves, and the moon kept watch over everyone. "
        "Now it is your turn. Breathe in slowly, two, three, four. Breathe out slowly, two, three, four. "
        "Let your toes rest. Let your hands rest. Let your eyes rest.{for_child} Sleep well, "
        "little dreamer. The forest will be here in the morning, and so will the stories."
    ),
    "id": (
        "Satu per satu, lampu-lampu hutan padam. Jangkrik memainkan lagu pelannya. "
        "{short} meringkuk di daun-daun lembut, dan bulan menjaga semua orang. "
        "Sekarang giliranmu. Tarik napas pelan-pelan, dua, tiga, empat. Hembuskan pelan-pelan, dua, tiga, empat. "
        "Biarkan jari kakimu istirahat. Biarkan tanganmu istirahat. Biarkan matamu istirahat.{for_child} "
        "Tidur yang nyenyak, pemimpi kecil. Hutan akan tetap ada besok pagi, begitu juga cerita-ceritanya."
    ),
}

FOR_CHILD = {
    "en": " This story was made just for you, {child}.",
    "id": " Cerita ini dibuat khusus untukmu, {child}.",
}

TITLE = {
    "en": "{short} and the {theme} Moon",
    "id": "{short} dan Bulan {theme}",
}


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def compose_story(animal: str, theme: str, language: str, child_name: str = "") -> dict:
    """Assemble a bedtime story. Returns dict with title and text."""
    animal = animal if animal in ANIMALS else "elephant"
    theme = theme if theme in THEMES else "kindness"
    language = language if language in ("en", "id") else "en"

    a = ANIMALS[animal][language]
    t = THEMES[theme][language]

    opening = OPENING[language].format(
        home=a["home"],
        name=a["name"],
        short=a["short"],
        cap_gift=_cap(a["gift"]),
    )
    scene = t["scene"].format(short=a["short"])
    action = t["action"].format(short=a["short"])
    lesson = t["lesson"]

    for_child = ""
    if child_name.strip():
        for_child = FOR_CHILD[language].format(child=child_name.strip())
    closing = CLOSING[language].format(short=a["short"], for_child=for_child)

    title = TITLE[language].format(short=a["short"], theme=t["label"])
    paragraphs = [opening, scene, action, lesson, closing]
    return {"title": title, "text": "\n\n".join(paragraphs)}


def options() -> dict:
    return {
        "animals": list(ANIMALS.keys()),
        "themes": list(THEMES.keys()),
        "theme_labels": {k: v["en"]["label"] for k, v in THEMES.items()},
        "theme_labels_id": {k: v["id"]["label"] for k, v in THEMES.items()},
    }

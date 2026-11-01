#Download a text and draw the 10 words that show up most often

import string
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import matplotlib.pyplot as plt
import requests


#book from the lecture, you can paste another link here
URL = "https://gutenberg.net.au/ebooks01/0100021.txt"
TOP = 10


def get_text(url: str) -> str | None:
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        print(f"Не вдалося завантажити текст: {error}")
        return None


def remove_punctuation(text: str) -> str:
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word: str) -> tuple[str, int]:
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text: str) -> dict[str, int]:
    #drop commas and dots, then Hello and hello become one word
    words = remove_punctuation(text).lower().split()

    #map and reduce run in threads, shuffle stays here to group pairs
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def visualize_top_words(word_counts: dict[str, int], top_n: int = TOP) -> None:
    #longest bar on top, like the picture in the task
    ranked = sorted(
        word_counts.items(), key=lambda item: item[1], reverse=True
    )
    top_words = ranked[:top_n]
    words = [word for word, _count in top_words]
    counts = [count for _word, count in top_words]

    plt.figure(figsize=(10, 6))
    plt.barh(words, counts, color="skyblue")
    plt.xlabel("Frequency")
    plt.ylabel("Words")
    plt.title("Top 10 Most Frequent Words")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    text = get_text(URL)
    if text:
        result = map_reduce(text)

        #the full dictionary is huge, so we only print the top
        print("Найчастіші слова:")
        ranked = sorted(result.items(), key=lambda item: item[1], reverse=True)
        for word, count in ranked[:TOP]:
            print(f"  {word}: {count}")

        visualize_top_words(result)

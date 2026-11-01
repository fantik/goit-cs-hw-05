#Copy files from a folder into subfolders by extension

import argparse
import asyncio
import logging
from pathlib import Path

#aiopath from the lecture dies on Python 3.14
#anyio.Path is the same kind of path
from anyio import Path as AsyncPath
from aioshutil import copyfile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Розкласти файли по теках за розширенням"
    )
    parser.add_argument("source", help="тека, з якої читаємо файли")
    parser.add_argument(
        "output",
        nargs="?",
        default="dist",
        help="тека, куди складаємо копії",
    )
    return parser.parse_args()


async def copy_file(file: AsyncPath, output: AsyncPath) -> int:
    #JPG and jpg go to one folder, a file with no extension goes to other
    extension = file.suffix.lower().lstrip(".") or "other"
    folder = output / extension
    try:
        await folder.mkdir(parents=True, exist_ok=True)
        await copyfile(file, folder / file.name)
        return 1
    except Exception as error:
        logging.error(f"не вдалося скопіювати {file}: {error}")
        return 0


async def read_folder(source: AsyncPath, output: AsyncPath) -> int:
    #read this folder, then the folders inside it
    try:
        entries = [item async for item in source.iterdir()]
    except Exception as error:
        logging.error(f"не вдалося прочитати {source}: {error}")
        return 0

    output_path = Path(output).resolve()
    tasks = []
    for item in entries:
        try:
            if await item.is_dir():
                #skip the output folder, otherwise we start copying the copies
                if Path(item).resolve() == output_path:
                    continue
                tasks.append(read_folder(item, output))
            elif await item.is_file():
                tasks.append(copy_file(item, output))
        except Exception as error:
            logging.error(f"пропускаю {item}: {error}")

    if not tasks:
        return 0

    counts = await asyncio.gather(*tasks)
    return sum(counts)


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(
        level=logging.ERROR,
        format="%(levelname)s: %(message)s",
    )

    #async paths, same idea as in the lecture
    source = AsyncPath(args.source)
    output = AsyncPath(args.output)
    source_path = Path(source).resolve()
    output_path = Path(output).resolve()

    if not source_path.is_dir():
        logging.error(f"такої теки немає: {source}")
    elif source_path == output_path:
        logging.error(f"вихідна і цільова тека збігаються: {source}")
    else:
        output_path.mkdir(parents=True, exist_ok=True)
        copied = asyncio.run(read_folder(source, output))
        print(f"Скопійовано файлів: {copied}. Вони лежать у {output}")

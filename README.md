# osu!parser

#### Парсинг рекордов и других данных с помощью osu!api v2

---

## Оглавление

- [Контакты](#контакты)
    - [Связь с разработчиком](#связь-с-разработчиком)
    - [Прочие ссылки](#прочие-ссылки)
- [Сборка и запуск](#сборка-и-запуск)
    - [Необходимые компоненты](#необходимые-компоненты)
    - [Первоначальная настройка](#первоначальная-настройка)
    - [PyInstaller](#pyinstaller)
- [Особые благодарности](#особые-благодарности)

---

## Контакты

#### Связь с разработчиком

- [Telegram для связи](https://t.me/diquoks)
- [Почта для связи](mailto:diquoks@yandex.ru)

#### Прочие ссылки

* [Руководство по использованию](GUIDE.md)

- [Статус разработки osu!parser](https://www.icloud.com/notes/0e0fiDVkllQ3CZ8kn6tbdpLnw)
- [Дизайн и используемые файлы](https://www.figma.com/community/file/1473682127614150983)
- [Telegram-канал с новостями](https://t.me/diquoks_channel)

---

## Сборка и запуск

### Необходимые компоненты

- [Git](https://git-scm.com/downloads)
- [Python](https://www.python.org/downloads)

### Первоначальная настройка

##### Клонируйте репозиторий git

```shell
git clone https://github.com/diquoks/osu-parser.git
```

##### Перейдите в корневую директорию

```bash
cd osu-parser
```

##### Установите зависимости

```bash
pip install -r requirements.txt
```

##### Перейдите в директорию `src`

```bash
cd src
```

##### Сгенерируйте файл `config.ini`

```shell
python main.py
```

##### Заполните `osu-parser/src/config.ini` и следуйте инструкциям для [PyInstaller](#pyinstaller)

### PyInstaller

##### Перейдите в директорию `build`

```shell
cd ../build
```

##### Создайте исполняемый файл

```shell
./build.sh
```

---

## Особые благодарности

Мои друзья, помогавшие мне находить баги и новые идеи для дальнейшей разработки osu!parser, спасибо вам <3

- Плейтестинг и багхантинг: [lofasolas](https://osu.ppy.sh/users/31543047), [LogiDASH](https://osu.ppy.sh/users/10335625), [Noity](https://osu.ppy.sh/users/34986222) и [zaharita_plays](https://osu.ppy.sh/users/33283996)
- Советы и идеи: [lofasolas](https://osu.ppy.sh/users/31543047), [LogiDASH](https://osu.ppy.sh/users/10335625) и [xChizhx](https://github.com/xchizhx)

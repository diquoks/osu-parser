## osu!parser

Программа на Python для парсинга информации об игроках и их рекордах в osu! с помощью osu!api v2

### Контакты

[Статус разработки osu!parser](https://www.icloud.com/notes/0e0fiDVkllQ3CZ8kn6tbdpLnw)

Telegram для связи:\
https://t.me/diquoks

Telegram-канал с новостями о разработке:\
https://t.me/diquoks_channel

Почта для связи:\
den232titovets@yandex.ru

## Руководство по использованию
![главное меню osu!parser](https://raw.githubusercontent.com/diquoks/osu-parser/refs/heads/main/assets/readme/main_menu.png)

osu!parser можно использовать как для парсинга последнего рекорда любого игрока, например для того чтобы узнать сколько pp получено при игре в мульти, так и для парсинга скрытой информации из статистики профиля или рекорда, например рекомендованного старрейта в профиле.

```Руководство актуально для всех патчей osu!parser версии 1.0.```

### Начало работы и настройка osu!parser

#### Настройка приложения

Отправка запросов в osu!parser требует данные вашего приложения OAuth для корректной работы.

![настройки приложения OAuth](https://raw.githubusercontent.com/diquoks/osu-parser/refs/heads/main/assets/readme/application_settings.png)

Для их получения [перейдите по ссылке](https://osu.ppy.sh/home/account/edit#oauth) и создайте своё приложение в разделе OAuth, а затем\
скопируйте ID и секретный ключ приложения и вставьте их в соответствующие поля в настройках.\
после чего нажмите на кнопку ```OK``` для сохранения. osu!parser не передаёт информацию о вашем\
приложении OAuth и хранит её исключительно на вашем компьютере в реестре Windows по пути:\
```HKEY_CURRENT_USER\Software\diquoks\osu!parser\Application```

#### Дополнительные настройки

![дополнительные настройки osu!parser](https://raw.githubusercontent.com/diquoks/osu-parser/refs/heads/main/assets/readme/additional_settings.png)

#### Переключатели

- Игнорировать Classic - мод Classic будет игнорироваться в парсинге (подходит для osu! stable).
- Учитывать фейлы - сфейленные рекорды также будут учитываться в парсинге.
- Расчёт pp за FC и SS - рядом со сложностью в парсинге будут показываться рассчитанные\
значения pp для FC (текущий рекорд без миссов и с полным комбо)\
и SS (текущий рекорд с максимальным количеством очков).
- Автомасштабирование - интерфейс osu!parser будет подгонять\
свою ширину, чтобы вместить все виджеты на экран.
- Поверх других окон - окно osu!parser не будет перекрываться другими окнами.

#### Директория osu!

Для работы калькулятора pp ему необходимы .osu файлы со сложностями.\
Обычно он использует их из папки со скачанными картами из директории osu!,\
но для начала её нужно выбрать: вы можете сделать это вручную или воспользоваться\
автопоиском (он ищет папку с именем ```osu!```, в которой бы находились ```osu!.exe``` и папка ```Songs```).

### Неочевидные функции и особенности интерфейса

В интерфейсе osu!parser используются кликабельные поля (номер версии, ссылки на сайт osu!),\
а также индикаторы (!), сигнализирующие о готовности или текущем выполнении\
каких-либо процессов во вкладках osu!parser (активный парсинг, его завершение или поиск директории).

### Смена языка / language change

Смена языка пока недоступна, ведь перед работой над ней нужно переписать код на customtkinter.\
The language change is not available yet, because I need to rewrite the code on customtkinter before working on it.

### Парсинг рекордов

![интерфейс парсинга рекордов в osu!parser](https://raw.githubusercontent.com/diquoks/osu-parser/refs/heads/main/assets/readme/last_score.png)

Позволяет парсить последний рекорд с сайта osu!, требует ID пользователя и режим osu!

- Быстрый режим - изменяет задержку между парсингом с 15 секунд на 3 секунды.

### Калькулятор pp

Калькулятор pp будет доступен после обновления 1.2, возвращайтесь сюда позже!

### Текстовый парсинг

![интерфейс текстового парсинга в osu!parser](https://raw.githubusercontent.com/diquoks/osu-parser/refs/heads/main/assets/readme/text_parsing.png)

Позволяет парсить все переменные профиля или рекорда,\
требует ID рекорда или профиля, а также режим osu!\
(osu!, osu!taiko, osu!catch, osu!mania), при парсинге профиля.

- Пустые значения - помещает все пустые переменные в конец файла вместо их игнорирования.

### Отдельные благодарности

В этом разделе хотел бы оставить ники моих друзей, помогавших мне находить\
баги и новые идеи для дальнейшей разработки osu!parser, спасибо вам <3

(Ники расположены в порядке убывания важности)

- Плейтестинг: lofasolas, LogiDASH, zaharita_plays и Noity
- Советы и идеи: LogiDASH, lofasolas и xChizhx
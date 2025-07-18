## Руководство по использованию osu!parser

`Руководство актуально для всех патчей osu!parser версии 1.1`\
`Следующее обновление руководства: версия 2.0`

![главное меню osu!parser](https://raw.githubusercontent.com/diquoks/osu-parser/refs/heads/master/code/assets/readme/main_menu.png)

osu!parser можно использовать для парсинга как рекордов любого игрока,\
так и для скрытых атрибутов из профиля или рекорда.

### Начало работы и настройка osu!parser

#### Настройка приложения

Отправка запросов в osu!parser требует данные вашего приложения OAuth для корректной работы.

![настройки приложения OAuth](https://raw.githubusercontent.com/diquoks/osu-parser/refs/heads/master/code/assets/readme/application_settings.png)

Для их получения [перейдите по ссылке](https://osu.ppy.sh/home/account/edit#oauth) и создайте своё приложение в разделе OAuth, а затем\
скопируйте ID и секретный ключ приложения и вставьте их в соответствующие поля в настройках.\
после чего нажмите на кнопку ```OK``` для сохранения. osu!parser не передаёт информацию о вашем\
приложении OAuth и хранит её исключительно на вашем компьютере в реестре Windows по пути:\
```HKEY_CURRENT_USER\Software\diquoks\osu!parser\Application```

#### Дополнительные настройки

![дополнительные настройки osu!parser](https://raw.githubusercontent.com/diquoks/osu-parser/refs/heads/master/code/assets/readme/additional_settings.png)

#### Переключатели

- Игнорировать Classic - мод Classic будет игнорироваться в парсинге (подходит для osu! stable).
- Учитывать фейлы - сфейленные рекорды также будут учитываться в парсинге.
- Расчёт pp за FC и SS - рядом со сложностью в парсинге будут показываться рассчитанные\
  значения pp для FC (текущий рекорд без миссов и с полным комбо)\
  и SS (текущий рекорд с максимальным количеством очков).
- Автомасштабирование - интерфейс osu!parser будет подгонять\
  свою ширину, чтобы вместить все виджеты на экран.
- Поверх других окон - окно osu!parser не будет перекрываться другими окнами.

### Неочевидные функции и особенности интерфейса

В интерфейсе osu!parser используются кликабельные поля (номер версии, ссылки на сайт osu!),\
а также индикаторы (!), сигнализирующие о текущем выполнении или окончании\
каких-либо процессов во вкладках osu!parser (активный парсинг или поиск директории, его завершение).

### Смена языка / language change

Смена языка пока недоступна, ведь перед работой над ней нужно переписать код на customtkinter.\
The language change is not available yet, because I need to rewrite the code on customtkinter before working on it.

### Парсинг рекордов

![интерфейс парсинга рекордов в osu!parser](https://raw.githubusercontent.com/diquoks/osu-parser/refs/heads/master/code/assets/readme/last_score.png)

Позволяет парсить последний рекорд с сайта osu!, требует ID пользователя и режим osu!

#### Переключатели

- Быстрый режим - изменяет задержку между парсингом с 15 секунд на 3 секунды.

### Калькулятор pp

Калькулятор pp пока недоступен, возвращайтесь сюда позже!

### Текстовый парсинг

![интерфейс текстового парсинга в osu!parser](https://raw.githubusercontent.com/diquoks/osu-parser/refs/heads/master/code/assets/readme/text_parsing.png)

Позволяет парсить все переменные профиля или рекорда,\
требует ID рекорда или профиля, а также режим osu!\
(osu!, osu!taiko, osu!catch, osu!mania), при парсинге профиля.

#### Переключатели

- Пустые значения - помещает все пустые переменные в конец файла вместо их игнорирования.

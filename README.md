# Hearthstone Deck Tracker под Wine: исправления и обновление

Состояние обновлено 11 августа 2026 года. Этот каталог — автономная документация и набор исходных патчей. Рабочие файлы HDT, Lutris и Hyprland остаются в своих системных каталогах; удаление этого каталога не отключит уже установленный фикс.

## Коротко: что делать обычно

Запускать в Lutris запись **Hearthstone + Deck Tracker**. Она сначала выполняет проверку совместимости, затем запускает Battle.net и HDT. Если Battle.net открылся, но игра не стартовала автоматически, нажать синюю кнопку Play.

Если overlay сломался уже во время матча: открыть Rofi через **Super+A**, найти **«Перезапустить HS Overlay»** и нажать Enter. Команда перезапускает только HDT прямо в активном Proton/UMU-сеансе Hearthstone; Hearthstone и текущий матч не закрываются.

В активной библиотеке Lutris оставлена ровно одна запись: **Hearthstone + Deck Tracker** (ID 4). Старые отдельные записи Battle.net, Hearthstone и Hearthstone Deck Tracker удалены только из библиотеки; общий Wine prefix и установленные файлы сохранены. Совместная запись больше не имеет `parent_slug`/`requires` и поэтому запускается самостоятельно.

Состояние до очистки сохранено в:

```text
/home/mike/.local/share/lutris/backups/pga-before-single-hs-entry-20260731-000804.db
/home/mike/.local/share/lutris/backups/lutris-shortcuts-before-single-hs-entry-20260731-000804.tar.zst
```

Проверить защиту и текущую сборку:

```bash
~/.local/share/lutris/scripts/hdt-prelaunch.py --status
```

Нормальный результат для зафиксированной сборки:

```text
executable: 41e8df362b951d81a0c4b897f1e264a7030bfc4ad90098bfa8c5fe2e45bbcc72
Wine button fix: yes
fixed overlay geometry: yes
Wine tooltip zero-state fix: yes
Wine window opacity-mask disabled: yes
Wine Battlegrounds click-through zone: yes
tooltip resource runtime: yes
Wine transparency fix: yes
known transparency layout: yes
working snapshot: valid
automatic updates: pinned by Wine compatibility guard
```

Автоматические обновления HDT специально закреплены. Для контролируемой попытки обновления используется одноразовое окно:

```bash
~/.local/share/lutris/scripts/hdt-prelaunch.py --enable-updates
```

Перед этим обязательно выполнить раздел «Обновление HDT» ниже: сделать датированную копию рабочего snapshot, полностью закрыть игру и запустить связку два раза. Обычный официальный exe без локальных geometry- и opacity-mask-marker будет сохранён как кандидат и автоматически откачен; принять новую версию можно только после переноса локальных source-патчей и сборки custom exe.

## Что лежит в этом каталоге

| Файл | Назначение |
|---|---|
| `README.md` | Эта инструкция |
| `hdt-prelaunch.py` | Точная резервная копия активного pre-launch guard |
| `hdt-wine-functional.patch` | Текущий единый функциональный source-патч для чистого HDT v1.55.3 |
| `hdt-wine-functional-v1.55.3.patch` | Версионная копия текущего патча для v1.55.3 |
| `hdt-wine-functional-v1.55.1.patch` | Историческая копия патча для v1.55.1 |
| `hdt-wine-functional-v1.55.0.patch` | Историческая копия патча для v1.55.0 |
| `hdt-wine-functional-v1.54.2.patch` | Историческая копия патча для v1.54.2 |
| `hdt-wine-functional-v1.53.6.patch` | Историческая копия прежнего патча для v1.53.6 |
| `upstream-pr-4741.patch` | Пять коммитов Wine-фикса кликов из PR #4741 |
| `local-hover-preview.patch` | Только локальная оптимизация hover и размещение превью слева |
| `local-fixed-overlay-position.patch` | Фиксация всей геометрии overlay после minimize/restore |
| `local-opacity-mask.patch` | Отключение несовместимой с Wine оконной маски увеличенной карты и Discover/Choose One |
| `local-clickthrough-zone.patch` | Принудительный click-through в центрально-левой игровой области Battlegrounds |
| `local-recent-games.patch` | Кнопка `Show more games`, последние 20 матчей и сохранение их финальных билдов |
| `PATCH-MANIFEST.txt` | Краткий исходный манифест установленной сборки |
| `MATERIALS.md` | Карта всех сохранённых материалов и автономное восстановление |
| `SHA256SUMS` | Контрольные суммы файлов набора и ключевых рабочих артефактов |
| `artifacts/hdt-working-v1.55.3-recent-games.tar.zst` | Текущий полный рабочий каталог HDT с историей 20 матчей |
| `artifacts/hdt-working-v1.55.3-recent-games.contents.sha256` | Хэши всех 169 файлов внутри текущего автономного снимка |
| `artifacts/hdt-working-v1.55.3-pre-chat.tar.zst` | Исторический рабочий каталог до экспериментов с чатом и новой истории игр |
| `config/hearthstone-plus-deck-tracker.yml` | Снимок конфигурации совместной записи Lutris |
| `config/hearthstone-deck-tracker.yml` | Исторический снимок удалённой отдельной записи HDT; в активную библиотеку не импортировать |
| `config/hdt-hearthstone-launcher.bat` | Совместный launcher Battle.net + HDT |
| `config/hyprland-hdt.conf` | Справочная копия только относящихся к HDT правил Hyprland |
| `config/wine-taskbar-icons.py` | Резервная копия active class/icon, geometry, routing и lifecycle guard |
| `config/hearthstone.desktop` | Desktop entry игры с постоянным `StartupWMClass` |
| `config/hearthstone-deck-tracker.desktop` | Desktop entry HDT с постоянным `StartupWMClass` |
| `config/restart-hs-overlay` | Безопасный перезапуск только HDT/overlay во время матча |
| `config/restart-hs-overlay.desktop` | Видимый пункт «Перезапустить HS Overlay» для Rofi |
| `assets/hearthstone-waybar.png` | Прозрачный master новой hand-drawn иконки Hearthstone для Waybar |

Текущий единый патч проверен на чистом исходном коммите `9e92f445f22d04f02c179c5cf6060f220dfe8929` (тег `v1.55.3`). Временные изменения проекта, необходимые только для сборки под Wine, и сгенерированные `.resources` в функциональные патчи не включены. Версионные копии прежних патчей сохранены для воспроизведения старых сборок; для текущей v1.55.3 использовать единый патч или `hdt-wine-functional-v1.55.3.patch`. Полный готовый к автономному восстановлению каталог находится в `artifacts/hdt-working-v1.55.3-recent-games.tar.zst`; его состав и порядок применения кратко описаны в `MATERIALS.md`.

## Зафиксированное рабочее состояние

Версия HDT: `1.55.3.7390`.

SHA-256 установленного исполняемого файла:

```text
41e8df362b951d81a0c4b897f1e264a7030bfc4ad90098bfa8c5fe2e45bbcc72
```

Основные пути:

```text
Wine prefix:
  /home/mike/Games/hs/battlenet

Каталог HDT:
  /home/mike/Games/hs/battlenet/drive_c/users/steamuser/AppData/Local/HearthstoneDeckTracker/Hearthstone Deck Tracker

Исполняемый файл:
  /home/mike/Games/hs/battlenet/drive_c/users/steamuser/AppData/Local/HearthstoneDeckTracker/Hearthstone Deck Tracker/Hearthstone Deck Tracker.exe

Конфигурация HDT:
  /home/mike/Games/hs/battlenet/drive_c/users/steamuser/AppData/Roaming/HearthstoneDeckTracker/config.xml

Активный guard:
  /home/mike/.local/share/lutris/scripts/hdt-prelaunch.py

Каталог резервных копий guard:
  /home/mike/.local/share/lutris/backups/hdt-overlay

Рабочий snapshot полного дерева HDT:
  /home/mike/.local/share/lutris/backups/hdt-overlay/working-current-wine

Полная резервная копия перед обновлением с v1.53.6 до v1.54.2:
  /home/mike/.local/share/lutris/backups/hdt-overlay/manual-before-v1542-upgrade-20260802-201029

Полная резервная копия перед обновлением с v1.54.2 до v1.55.0:
  /home/mike/.local/share/lutris/backups/hdt-overlay/manual-before-v1550-upgrade-20260804-2145

Полная резервная копия перед обновлением с v1.55.0 до v1.55.1:
  /home/mike/.local/share/lutris/backups/hdt-overlay/manual-before-v1551-upgrade-20260805-152003

Полная резервная копия перед обновлением с v1.55.1 до v1.55.3:
  /home/mike/.local/share/lutris/backups/hdt-overlay/manual-before-v1553-upgrade-20260810-114440

Текущая рабочая копия v1.55.3, восстановленная после полного отката экспериментов с чатом:
  /home/mike/.local/share/lutris/backups/hdt-overlay/manual-before-chat-clickthrough-20260810-173111

Полная резервная копия перед добавлением истории последних 20 игр:
  /home/mike/.local/share/lutris/backups/hdt-overlay/manual-before-recent-games-20260811-140706

Полная резервная копия до исправления Battlegrounds:
  /home/mike/.local/share/lutris/backups/hdt-before-bg-fix-20260710-1136.tar.zst

Class/icon и geometry guard:
  /home/mike/.config/waybar/scripts/wine-taskbar-icons.py

Desktop entries:
  /home/mike/.local/share/applications/hearthstone.desktop
  /home/mike/.local/share/applications/hearthstone-deck-tracker.desktop

Локальные fallback-иконки:
  /home/mike/.local/share/icons/hicolor/*/apps/hearthstone-hand-drawn.png
  /home/mike/.local/share/icons/hicolor/*/apps/hearthstone-deck-tracker.png
```

Установленный `Hearthstone Deck Tracker.exe` и `untapped-scry-dotnet.dll` сейчас оба PE32+ x86-64. Рабочий snapshot занимает около 76 МБ, архив до исправления — около 19 МБ.

## Какие проблемы были и что исправлено

### 1. Фиолетовый, затем непрозрачный чёрный overlay

Полностью прозрачный фон WPF-окна `HearthstoneOverlay` некорректно композировался Wine/XWayland: вместо прозрачности появлялся фиолетовый или чёрный полноэкранный прямоугольник.

Перед каждым запуском guard ищет в PE ровно одну UTF-16LE-строку фоновой кисти `#4C0000FF` и заменяет её на `#01000000`. Длины строк одинаковы, поэтому смещения PE не меняются. Альфа `1/255` обходит Wine-баг, но визуально фон остаётся прозрачным.

Дополняющие правила Hyprland:

- для `HearthstoneOverlay` заданы `opacity = 1`, `no_blur`, `no_shadow`, `no_dim`, `no_anim`, отсутствие рамки и `opaque = false`;
- для Hearthstone отключено неактивное тонирование;
- правило не забирает управление мышью у самого HDT: динамический click-through продолжает переключать трекер.

Нельзя ставить для overlay `opaque = true`: это снова делает почти прозрачный фон видимым. Также нельзя задавать `no_focus`, `no_input` или `no_follow_mouse` для `HearthstoneOverlay`: эти эксперименты ухудшали фокус и кликабельность WPF-панелей HDT.

### 2. Пустые панели в Battlegrounds

Причиной оказался частично обновлённый каталог: x64 HDT был смешан с x86 `untapped-scry-dotnet.dll`. Трекер запускался, но Scry не мог читать состояние Battlegrounds, поэтому окна оставались пустыми.

Изначально было синхронизировано полное официальное дерево v1.53.6 одной архитектуры. 2 августа 2026 года оно целиком обновлено до v1.54.2, 4 августа — до v1.55.0, 5 августа — до v1.55.1, а 10 августа — до v1.55.3; после каждого обновления устанавливался функционально исправленный x64 exe из точно того же тега. Guard сравнивает PE machine type главного exe и Scry DLL. Несовпадающее обновление не принимается.

Важно: нельзя переносить отдельные DLL между выпусками или копировать старый custom exe поверх произвольного нового набора зависимостей. Обновляется полное дерево одного выпуска, затем для этого же исходного тега собирается custom exe.

### 3. Правая панель Battlegrounds не принимала клики

Стандартные WPF `Button`/`ButtonBase` ненадёжно получают `Click` внутри overlay с `WS_EX_TRANSPARENT` под Wine. Применена серия из пяти коммитов [HearthSim/Hearthstone-Deck-Tracker PR #4741](https://github.com/HearthSim/Hearthstone-Deck-Tracker/pull/4741), итоговый коммит `7b32e0c164b5c751a01a61b8d664320ff4533768`.

Кнопки Battlegrounds заменены на `OverlayButton : Border`, обрабатывающий `MouseLeftButtonUp`. Исправлены вкладки справа, закрепление миньонов, фильтры, comps и связанные элементы. В сборку также входит regression test, запрещающий возврат обычных WPF-кнопок в этих overlay-представлениях.

### 4. Низкий FPS и нулевое состояние самого tooltip

Анимация увеличения и fade tooltip заставляла Wine/WPF перекомпоновывать полноэкранное прозрачное окно на каждом кадре. Более того, Wine иногда пропускал переход из начального `ScaleX/ScaleY=0` или `Opacity=0`; в результате dirty rectangle превью оставался непрозрачным чёрным прямоугольником.

В `Controls/Tooltips/CardTooltip.xaml` полностью убраны нулевые начальные состояния и обслуживающие их show/hide/fade storyboard. Изображение карты создаётся сразу в конечном видимом состоянии, поэтому нет покадровой полноэкранной перекомпоновки и Wine не застревает на нулевом состоянии самого tooltip. Бинарный маркер исправления: `HDT_WINE_TOOLTIP_NO_ZERO_STATE`.

### 5. Чёрные прямоугольники на любой карте и в Choose One/Discover

Оставшийся дефект оказался отдельным от `CardTooltip`. `OverlayWindow.SetCardOpacityMask()` вырезает из полноэкранного overlay прямоугольник над собственной увеличенной картой Hearthstone, а `SetDiscoverCardOpacityMask()` вырезает по одному прямоугольнику над каждым вариантом выбора. В исходной реализации `OverlayOpacityMask.CreateOpacityMask()` такие исключённые области имели alpha ровно `0`. Wine/XWayland показывал их как непрозрачный чёрный цвет. Поэтому размер одного прямоугольника совпадал с увеличенной картой, а при `Choose One` одновременно появлялись три одинаковых прямоугольника.

Первая попытка оставить в вырезах alpha `1/255` не помогла: значение умножалось на уже почти прозрачный фон окна (`1/255`) и при итоговой 8-битной композиции снова округлялось до нуля. Поэтому в Wine-сборке `Utility/Overlay/OverlayOpacityMask.cs` вообще не назначает динамическую оконную `OpacityMask` и всегда возвращает `Mask = null`. Панели и собственные tooltip HDT продолжают управлять видимостью штатно; отключены только проблемные прямоугольные «вырезы» над картами Hearthstone. Исправление действует для обычного hover и для любого числа вариантов Discover/Choose One. Бинарный маркер: `HDT_WINE_OPACITY_MASK_DISABLED`.

Это изменение хранится отдельно в `local-opacity-mask.patch`, включено в `hdt-wine-functional.patch` и обязательно для каждой будущей custom-сборки.

Финальный вариант проверен 2 августа 2026 года в живом матче Battlegrounds: после перезапуска HDT чёрные прямоугольники исчезли.

### 6. Центрально-левая область забирала курсор и клики

В отмеченной пользователем части игрового поля обычный курсор Hearthstone иногда заменялся системным курсором WPF, а клики переставали доходить до игры. Диагностическая сборка проверила все зарегистрированные HDT hit-test-элементы и X11-окно под курсором: настоящих интерактивных панелей tracker в этой области нет. Дефект был временно залипшим состоянием полноэкранного `HearthstoneOverlay`, которое снимало `WS_EX_TRANSPARENT` для чужой области.

В `Windows/OverlayWindow.MouseOverDetection.cs` добавлена принудительная WPF/Win32 click-through-область `Rect(250, 140, 1300, 620)`. Она покрывает всю отмеченную центрально-левую часть при текущей фиксированной геометрии DP-1. Перед вызовом `SetClickthrough` случайные clickable-hit в этой зоне отбрасываются. Область действует постоянно, а не только при `_game.IsBattlegroundsMatch`: при входе в Battlegrounds, выходе в его меню и переходах между сценами этот флаг кратковременно становится `false`, из-за чего прежний фикс иногда отключался. Левая панель статистики находится левее, Bob's Buddy выше, правая панель далеко правее, поэтому их интерактивность сохраняется. Бинарный маркер: `HDT_WINE_BATTLEGROUNDS_CLICKTHROUGH_ZONE`.

Попытки отдельно исправить внутриигровой чат Battle.net 10–11 августа полностью откачены: широкая нижняя click-through-зона, возврат фокуса, X11 RECORD-listener, `no_follow_mouse` и `cursor:no_warps` ухудшали работу основного overlay, но не обеспечивали стабильный ввод. Их нельзя переносить в будущие сборки.

Исправление хранится в `local-clickthrough-zone.patch` и включено в общий `hdt-wine-functional.patch`. Как и фиксированная геометрия, координаты привязаны к текущему monitor layout и должны быть пересчитаны при смене масштаба или разрешения.

### 7. Превью карты уходило за правый край экрана

В `AnimatedCard` и `AnimatedCardList` добавлена передача `CardTooltipPlacement`. Для правой панели миньонов Battlegrounds в `BattlegroundsCardsGroup.xaml` явно задано `CardTooltipPlacement="Left"`. Остальные списки сохраняют исходное значение `Right`.

### 8. Bob's Buddy и счётчики уезжали вправо

После minimize/restore Wine один раз сообщил HDT размер виртуального рабочего стола вместо client area Hearthstone. `OverlayWindow.UpdatePosition()` принял его без проверки: окно игры оставалось `(11,50) 2730×1091`, а `HearthstoneOverlay` разрастался примерно до `4264×1161`. Bob's Buddy центрировался уже по ошибочной ширине, а нижний `PlayerCounters` со значением вроде tavern spell `+9/+10` пересчитывался через тот же неправильный размер.

В локальной сборке геометрия всего overlay теперь неизменна:

```text
Win32/X11, используемые WPF: 3453,62 3412x1363
Hyprland при scale 1.25:      примерно 11,50 2730x1091
Ожидаемое окно overlay:       примерно 10,49 2729x1090
Binary marker:                HDT_WINE_FIXED_OVERLAY_2730X1091
```

При состоянии Hearthstone `Minimized` геометрия вообще не считывается. При restore, событиях окна и обычных обновлениях layout HDT повторно применяет только зафиксированный прямоугольник. Цикл minimize/restore проверен: координаты и размер overlay не изменились.

Этот фикс намеренно привязан к текущему DP-1, масштабу 1.25 и расположению игры. При изменении layout мониторов или масштаба нужно заново измерить Win32/X11 rectangle и обновить четыре константы `WineFixedOverlay*` в `Windows/OverlayWindow.Update.cs`.

### 8a. Пропали вероятности Bob's Buddy и нижние Battlegrounds-счётчики

После обновления Hearthstone старая HDT v1.53.6 продолжала читать `Power.log`, но её версия `HearthMirror` возвращала пустой `MatchInfo`. В журнале HDT это проявлялось как `BobsBuddyInvoker.SetupInputPlayer >> System.ArgumentException: Player`: локальная сущность игрока не попадала в модель матча, поэтому Bob's Buddy не мог сформировать вход симуляции, а связанные Battlegrounds-счётчики spell damage и blood gems также оставались без данных.

2 августа 2026 года установлено полное официальное дерево [HDT v1.54.2](https://github.com/HearthSim/Hearthstone-Deck-Tracker/releases/tag/v1.54.2) с его согласованными версиями `HearthMirror`, `HearthDb`, `BobsBuddy`, `BobsBuddy.Common` и `HSReplay`, затем поверх исходников v1.54.2 заново собран и установлен custom exe со всеми Wine-исправлениями из этого каталога. Нельзя лечить этот сбой заменой одной DLL: exe, managed-зависимости и native-файлы должны происходить из одного выпуска.

### 8b. История последних игр была ограничена текущей сессией

Панель `Latest Games` по-прежнему по умолчанию показывает до восьми матчей текущей сессии и сохраняет прежний компактный вид. Под списком появляется Wine-совместимая кнопка `Show more games`, если в истории есть дополнительные матчи. Она раскрывает до 20 последних игр текущего режима (обычный Battlegrounds или Duos); `Show session games` возвращает компактный сессионный список.

Все строки используют штатный `BattlegroundsGameView`, поэтому для дополнительных игр сохраняются герой, место, изменение MMR и финальный билд при наведении. Очистка истории по возрасту больше не удаляет последние 20 игр: записи старше семи дней удаляются только сверх этого минимума. Изменение и три теста хранения находятся в `local-recent-games.patch` и включены в общий `hdt-wine-functional.patch`.

### 9. Вместо иконок HDT и Hearthstone в Waybar были вопросики

UMU/Proton назначал игре, HDT и их служебным XWayland-окнам один `WM_CLASS`: `steam_app_default`. Модуль `wlr/taskbar` подбирает иконку по этому значению и не может различить два приложения, поэтому показывал fallback со знаком вопроса.

Для иконок активный `wine-taskbar-icons.py` выполняет четыре точечных действия:

- окну с точным заголовком `Hearthstone` назначает класс `hearthstone-hand-drawn`;
- окну с точным заголовком `Hearthstone Deck Tracker` назначает класс `hearthstone-deck-tracker`;
- пустому служебному Wine-окну физического размера `160×20` выставляет `_NET_WM_STATE_SKIP_TASKBAR`.
- прозрачному `HearthstoneOverlay` также выставляет `_NET_WM_STATE_SKIP_TASKBAR`, чтобы оно не создавало третью кнопку рядом с игрой и HDT.

`HearthstoneOverlay`, `Session Recap`, `Hidden Window` и остальные окна HDT скрипт не переименовывает. Это важно: правило прозрачности overlay по-прежнему сопоставляется с `steam_app_default`.

Для обоих новых классов установлены desktop entries. Для Hearthstone используется выбранная пользователем [Color Hand Drawn icon от Icons8](https://icons8.com/icon/Undt8wxX4y4V/hearthstone): белые углы исходного JPG сделаны прозрачными, а обработанный master сохранён как `assets/hearthstone-waybar.png`. Уникальные `Icon=` и `StartupWMClass=hearthstone-hand-drawn` не дают теме Tela снова подменить значок. В `hicolor` установлены варианты 16, 22, 24, 32, 48, 64, 128, 256 и 512 пикселей. Иконка HDT по-прежнему берётся из штатного `Images/HearthstoneDeckTracker.ico`. Скрипт запускается из `~/.config/hypr/userprefs.conf` через `exec-once` и защищён lock-файлом от дубликатов.

В итоговом `wlr/taskbar` это две разные кнопки: чёрно-белая спираль с `app_id=hearthstone-deck-tracker` относится к HDT, а жёлто-синий hand-drawn квадрат с `app_id=hearthstone-hand-drawn` — к самой игре. Служебный `steam_app_default` overlay скрыт. Это проверено временным диагностическим форматом `{icon} {app_id}`, после чего обычный формат `{icon}` был восстановлен.

Этот фикс не требует изменения конфигурации Waybar. Он переживает пересборку `includes.json`, смену layout Waybar и обычное обновление HDT, поскольку скрипт, desktop entries и уже сгенерированные PNG находятся вне Wine prefix. Повторное восстановление нужно только после удаления пользовательских конфигов/иконок или полного переноса системы.

### 10. Fullscreen или ручной resize скрывал и смещал tracker

Воспроизведены две независимые причины:

- настоящий compositor fullscreen менял Hearthstone с рабочего `2730×1091` на весь DP-1 `2752×1152` и размещал игру выше прозрачного overlay, поэтому tracker полностью исчезал;
- прямой X11 configure-запрос обходил даже `min_size`/`max_size` Hyprland и мог уменьшить `HearthstoneOverlay`, например, до `833×571`. Внутренний source-фикс HDT уже успевал записать правильную геометрию, поэтому не получал нового события и не исправлял последующий внешний resize.

Защита теперь работает на двух уровнях. Правила Hyprland задают начальные размеры, `fullscreen_state = 0 0`, блокируют `fullscreen`/`maximize`/`fullscreenoutput` от приложений и закрепляют допустимые размеры. Запущенный `wine-taskbar-icons.py` раз в секунду проверяет фактическое состояние и восстанавливает:

```text
Hearthstone:
  workspace 5, tiled, not fullscreen
  Hyprland: 11,50 2730x1091

HearthstoneOverlay:
  workspace 5, floating, not fullscreen
  X11:       3453,62 3412x1363
  Hyprland:  10,49 2729x1090

HDT main window:
  workspace 3, floating, not fullscreen
  X11:       3612,72 1200x675
  Hyprland:  138,58 960x540
```

Если внешний инструмент всё же включает fullscreen, guard снимает оба fullscreen-state, возвращает прежний фокус и повторно применяет X11 rectangle. `Super+F` переопределён через режим `--toggle-fullscreen`: для трёх защищённых окон он оставляет стабильный layout, для всех остальных приложений продолжает работать как обычный fullscreen.

Таким образом, настоящий fullscreen для Hearthstone/HDT намеренно запрещён: он несовместим с проверенной фиксированной геометрией overlay. Нормальный tiled-режим Hearthstone уже занимает всю доступную область DP-1, кроме Waybar. Ручной move/resize может быть виден не более одного цикла guard (до одной секунды), после чего окно возвращается на место.

Это внешний конфигурационный слой вне Wine prefix, поэтому обычное обновление HDT его не удаляет. При изменении монитора, scale или расположения DP-1 нужно синхронно пересчитать и внутренние `WineFixedOverlay*`, и `X11_GEOMETRIES` в guard.

### 11. Battle.net открывался не рядом с Lutris

Battle.net в UMU-prefix использует тот же общий `steam_app_default`, что и другие Wine-окна, поэтому простое правило по class затронуло бы Hearthstone или служебные окна. Кроме того, статический Hyprland-rule не умеет выразить отношение «workspace другого уже открытого приложения».

В активный window guard добавлена отдельная синхронизация:

1. Battle.net распознаётся по сочетанию заголовка `Battle.net`, Wine class и, при необходимости, командной строке `Battle.net.exe`/`Battle.net Launcher.exe`. `Battle.net Helper.exe` и `Agent.exe` исключены.
2. Среди окон с class `net.lutris.Lutris` или `lutris` выбирается наиболее недавно активное.
3. Battle.net перемещается на workspace этого окна Lutris через `movetoworkspacesilent`, не переключая текущий workspace пользователя.
4. Если подходящего окна Lutris нет или его workspace невозможно определить, используется workspace 3.

Синхронизация выполняется постоянно, поэтому при переносе Lutris Battle.net следует за ним максимум через одну секунду. В `userprefs.conf` также есть статический `battlenet_workspace_fallback`, который немедленно направляет подходящее новое окно на workspace 3 до первого цикла guard.

Hearthstone этой логикой не затрагивается: matcher Battle.net явно не принимает его заголовок/процесс, а отдельный `PROTECTED_WINDOWS` по-прежнему принудительно держит `Hearthstone` на workspace 5. Интеграционный тест выполнен с временным XWayland-окном `Battle.net / steam_app_default`: при Lutris на workspace 4 тестовое окно последовало на 4, после чего Lutris был возвращён на 3.

### 12. HDT оставался работать после закрытия Hearthstone

Window guard теперь содержит lifecycle state machine. Она намеренно не закрывает HDT просто из-за отсутствия игрового окна: Battle.net может ещё запускать игру, а пользователь может открыть tracker отдельно.

Автозакрытие активируется только после того, как текущий экземпляр guard действительно увидел окно или процесс `Hearthstone.exe`. После исчезновения и окна, и процесса игры:

1. начинается grace period 6 секунд;
2. если Hearthstone вернулся, ожидаемое закрытие полностью отменяется;
3. если игра не вернулась, главному окну `Hearthstone Deck Tracker` отправляется обычный `WM_CLOSE`;
4. при текущем `<CloseToTray>false</CloseToTray>` HDT вызывает `Core.Shutdown()`, сохраняет конфиг, статистику, колоды и настройки плагинов;
5. только если чистое завершение не закончилось ещё за 15 секунд, guard отправляет `SIGTERM` оставшемуся процессу HDT.

После исчезновения HDT lifecycle-state сбрасывается. Поэтому следующий отдельный запуск tracker снова безопасно ждёт фактического запуска Hearthstone. Если сам guard был перезапущен уже после закрытия игры, он также не убивает существующий HDT: это безопасное поведение против ложного срабатывания.

Переходы записываются только при событиях в `$XDG_RUNTIME_DIR/hdt-autoclose.log`; постоянного ежесекундного лог-спама нет. End-to-end тест на временных XWayland-окнах подтвердил: игра была замечена, после её закрытия начался timer, через 7 секунд был отправлен `WM_CLOSE`, ещё через секунду тестовый tracker исчез.

### 13. После обновления системы Lutris перестал видеть executable

Обновление CachyOS от 20 июля 2026 года установило Lutris `0.5.22-2`. В этой сборке путь конфигурации выбирается при старте: если существует `~/.config/lutris`, она считается полным legacy-корнем; если каталога нет, используется `~/.local/share/lutris`.

До обновления в `~/.config/lutris` лежал только наш `scripts/hdt-prelaunch.py`, тогда как БД и игровые YAML находились в `~/.local/share/lutris`. В результате Lutris находил запись **Hearthstone + Deck Tracker** в `pga.db`, но искал её YAML в пустом `~/.config/lutris/games`. В логе это проявлялось как:

```text
The game doesn't have an executable
This game has no executable set. The install process didn't finish properly.
```

Рабочая структура теперь приведена к одному корню:

```text
~/.local/share/lutris/pga.db
~/.local/share/lutris/games/*.yml
~/.local/share/lutris/scripts/hdt-prelaunch.py
```

Единственная совместная запись HDT указывает на новый путь guard. Ложный `~/.config/lutris` убран из активного пути; его диагностическая копия сохранена как `~/.config/lutris.pre-xdg-fix-20260720-1330`. Не следует заново создавать именно каталог `~/.config/lutris` только ради пользовательских скриптов: это снова переключит весь Lutris на пустой legacy-корень.

После исправления новый объект `LutrisConfig` подтвердил `CONFIG_DIR=/home/mike/.local/share/lutris`, executable `drive_c/hdt-hearthstone-launcher.bat` и правильный prelaunch path. Реальный запуск дошёл до UMU/GE-Proton, открыл HDT и окно Battle.net без прежней ошибки.

## Настройки HDT, важные для Battlegrounds

В рабочем `config.xml` подтверждены следующие значения:

```xml
<HideOverlay>false</HideOverlay>
<VisibleOverlay>true</VisibleOverlay>
<OverlayCardAnimations>true</OverlayCardAnimations>
<OverlayCardToolTips>true</OverlayCardToolTips>
<CardImageSize>1</CardImageSize>
<RunBobsBuddy>true</RunBobsBuddy>
<ShowBobsBuddyDuringCombat>true</ShowBobsBuddyDuringCombat>
<ShowBobsBuddyDuringShopping>false</ShowBobsBuddyDuringShopping>
<CloseToTray>false</CloseToTray>
<MinimizeToTray>false</MinimizeToTray>
```

`CheckForUpdates` может временно оказаться `true`, если уже запущенный старый процесс HDT записал свою конфигурацию при выходе. Источник истины — файл-маркер `PIN_AUTOMATIC_UPDATES` и результат `hdt-prelaunch.py --status`: перед следующим запуском guard снова запишет `false`.

## Как работает защита обновлений

Pre-launch script подключён к обеим записям Lutris через `prelaunch_command` и `prelaunch_wait: true`.

При каждом запуске он выполняет следующее:

1. Управляет закреплением updater и одноразовой попыткой обновления.
2. Проверяет наличие fully-qualified маркера `Hearthstone_Deck_Tracker.Controls.Overlay.Battlegrounds.OverlayButton` в exe.
3. Проверяет локальный UTF-16LE-маркер фиксированной геометрии `HDT_WINE_FIXED_OVERLAY_2730X1091`.
4. Проверяет маркеры `HDT_WINE_TOOLTIP_NO_ZERO_STATE`, `HDT_WINE_OPACITY_MASK_DISABLED` и `HDT_WINE_BATTLEGROUNDS_CLICKTHROUGH_ZONE`.
5. Проверяет наличие пяти DLL, нужных новой сборке для preserialized WPF-ресурсов.
6. Проверяет, что бинарный layout прозрачной кисти известен: присутствует ровно исходный или уже исправленный вариант.
7. Сравнивает архитектуру `Hearthstone Deck Tracker.exe` и `untapped-scry-dotnet.dll`.
8. При необходимости создаёт резервную копию exe и применяет минимальную transparency-замену.
9. После успешной проверки копирует полное дерево HDT в `working-current-wine`.
10. Если обновление несовместимо, сохраняет его полное дерево в `rejected-updates/<sha256>/` и атомарно возвращает последний рабочий snapshot.

Команды управления:

```bash
# Только показать состояние; ничего не изменяет
~/.local/share/lutris/scripts/hdt-prelaunch.py --status

# Разрешить ровно одну попытку официального обновления
~/.local/share/lutris/scripts/hdt-prelaunch.py --enable-updates

# Немедленно снова закрепить рабочую сборку
~/.local/share/lutris/scripts/hdt-prelaunch.py --disable-updates
```

Файлы состояния:

```text
~/.local/share/lutris/backups/hdt-overlay/PIN_AUTOMATIC_UPDATES
~/.local/share/lutris/backups/hdt-overlay/ONE_SHOT_UPDATE_ATTEMPT
```

Переменная `HDT_ALLOW_UNPATCHED_UPDATE=1` является внутренним аварийным обходом этапа автоматического отката. При обычном использовании её задавать нельзя: такой запуск не входит в проверенный сценарий и всё равно может быть остановлен следующими проверками перед созданием snapshot.

### Ограничение автоматической проверки

Guard надёжно проверяет Wine-кнопки, фиксированную геометрию, tooltip без нулевого состояния, отключение несовместимой оконной opacity mask, центральную click-through-зону, runtime-зависимости, поддерживаемую transparency-кисть и совпадение архитектуры. Он не умеет доказать по универсальному бинарному маркеру только позицию превью слева.

Следствие: обычный официальный выпуск без локальных geometry-, opacity-mask- и click-through-marker будет автоматически отклонён даже после включения upstream `OverlayButton`. Это сделано намеренно: дрейф центральных элементов, чёрные карточные прямоугольники и мёртвая зона мыши не смогут незаметно вернуться. Чтобы принять новый выпуск, сначала перенести `local-fixed-overlay-position.patch`, `local-hover-preview.patch`, `local-opacity-mask.patch` и `local-clickthrough-zone.patch` на его исходники, собрать custom exe и только затем обновить рабочее дерево. Датированный snapshot перед обновлением всё равно обязателен.

## Обновление HDT: безопасная последовательность

### Шаг 1. Полностью закрыть приложения

Закончить матч и закрыть Hearthstone, HDT и Battle.net. Не обновлять файлы во время работы Wine-процессов.

Проверка:

```bash
pgrep -a -f '^C:.*Hearthstone Deck Tracker.exe$|^C:.*Hearthstone.exe -launch|Battle.net'
```

Команда не должна показывать HDT или Hearthstone. Если виден только несвязанный процесс, проверить его вручную; не завершать процессы вслепую.

### Шаг 2. Проверить и сохранить текущий snapshot

```bash
~/.local/share/lutris/scripts/hdt-prelaunch.py --status

BACKUP_ROOT="$HOME/.local/share/lutris/backups/hdt-overlay"
STAMP="$(date +%Y%m%d-%H%M%S)"
cp -a --reflink=auto \
  "$BACKUP_ROOT/working-current-wine" \
  "$BACKUP_ROOT/manual-before-update-$STAMP"
```

Запомнить напечатанный путь `manual-before-update-...`. Эта копия нужна потому, что совместимое обновление становится новым `working-current-wine` сразу после проверки.

### Шаг 3. Открыть одноразовое окно обновления

```bash
~/.local/share/lutris/scripts/hdt-prelaunch.py --enable-updates
~/.local/share/lutris/scripts/hdt-prelaunch.py --status
```

Ожидаемый статус updater: `enabled for one update attempt`.

### Шаг 4. Первый запуск

Запустить в Lutris **Hearthstone + Deck Tracker**. Первый pre-launch разрешит HDT проверить наличие официального обновления. Дождаться установки или сообщения об отсутствии обновления.

После завершения updater снова полностью закрыть Hearthstone, HDT и Battle.net. Даже если updater сам перезапустил HDT, ручной следующий запуск необходим для проверки новой версии guard-скриптом.

### Шаг 5. Второй запуск и автоматическая проверка

Снова запустить **Hearthstone + Deck Tracker**.

Возможны три результата:

- обновление не было найдено — guard снова закрепит текущую сборку;
- обновление содержит `OverlayButton`, geometry-marker, tooltip-marker, opacity-mask-marker и click-through-marker, имеет знакомый layout прозрачности и согласованную архитектуру — guard применит transparency patch, сделает его новым snapshot и снова закрепит updater;
- обновление несовместимо — guard сохранит его в `rejected-updates/<sha256>/`, вернёт предыдущий `working-current-wine` и закрепит updater.

### Шаг 6. Проверка после обновления

```bash
~/.local/share/lutris/scripts/hdt-prelaunch.py --status

file \
  '/home/mike/Games/hs/battlenet/drive_c/users/steamuser/AppData/Local/HearthstoneDeckTracker/Hearthstone Deck Tracker/Hearthstone Deck Tracker.exe' \
  '/home/mike/Games/hs/battlenet/drive_c/users/steamuser/AppData/Local/HearthstoneDeckTracker/Hearthstone Deck Tracker/untapped-scry-dotnet.dll'
```

В статусе button fix, fixed overlay geometry, tooltip zero-state, window opacity-mask disabled, Battlegrounds click-through zone, transparency fix и transparency layout должны быть `yes`, snapshot — `valid`, обновления — `pinned`. Обе PE-библиотеки должны быть одной архитектуры.

В тестовом матче Battlegrounds проверить:

1. Нет чёрного или фиолетового полноэкранного фона.
2. Панели игрока и противника заполняются данными.
3. Вкладки и кнопки правой панели нажимаются.
4. Hover-preview появляется без тяжёлой анимации и без чёрного прямоугольника при длительном наведении на любую карту.
5. При Discover/Choose One все варианты видны; чёрные прямоугольники поверх предложенных карт не появляются.
6. Preview карт правой панели открывается слева и целиком остаётся на экране.
7. Bob's Buddy появляется в бою и вместо бесконечного индикатора показывает проценты win/tie/loss.
8. Нижняя панель показывает актуальные бонусы spell damage и blood gems.
9. После minimize/restore Bob's Buddy остаётся по центру, а нижний счётчик эффектов не сдвигается вправо.
10. В центрально-левой части доски сохраняется курсор Hearthstone, а клики проходят в игру.

После успешной проверки датированную backup-копию лучше оставить хотя бы до следующего патча HDT.

## Перезапуск overlay через Rofi

Для восстановления сломанного overlay без закрытия текущего матча:

1. Нажать **Super+A**.
2. Ввести `HDT`, `overlay`, `Hearthstone` или `перезапустить`.
3. Выбрать **«Перезапустить HS Overlay»**.
4. Дождаться уведомления **«HS Overlay перезапущен»**. Обычный запуск занимает несколько секунд, но проверка ждёт появление окна до 60 секунд.

Скрипт сначала убеждается, что Hearthstone действительно запущен. Затем он отправляет `WM_CLOSE` только главному окну HDT, ждёт чистое завершение, выполняет обычный `hdt-prelaunch.py` и запускает HDT через `umu-run` с `PROTON_VERB=runinprefix`. Путь используемого Proton и runtime-переменные копируются из живого процесса Hearthstone, а Wine prefix жёстко остаётся `/home/mike/Games/hs/battlenet`. Если главное окно HDT уже исчезло вместе со сломанным overlay или чистое завершение зависло, сигнал отправляется только живому Windows-процессу, у которого `argv[0]` оканчивается ровно на `Hearthstone Deck Tracker.exe`. Упоминание этого пути в аргументах Lutris/UMU не считается совпадением, а zombie-процессы игнорируются. Скрипт намеренно не вызывает `wineserver -k`, не завершает общие Wine/Proton-процессы и не трогает `Hearthstone.exe`.

Дополнительные предохранители:

- вне запущенного Hearthstone команда ничего не запускает и показывает уведомление;
- lock-файл не позволяет двум случайным нажатиям выполнять перезапуск одновременно;
- после остановки HDT ещё раз проверяется, что игра осталась запущена;
- успешным считается только запуск, при котором устойчиво появилось окно `HearthstoneOverlay`;
- если у живого Hearthstone невозможно получить корректный `PROTONPATH`, запуск безопасно отменяется;
- прямой запуск всё равно проходит через pre-launch compatibility guard и тот же рабочий Wine prefix.

Диагностический лог текущего сеанса:

```bash
cat "$XDG_RUNTIME_DIR/hdt-overlay-restart.log"
```

Пункт Rofi и скрипт находятся вне Wine prefix, поэтому обычное обновление HDT их не удаляет. Они больше не зависят от ID записи Lutris, поэтому после пересоздания или переименования совместного ярлыка исправлять скрипт не требуется.

Этот быстрый перезапуск предназначен для исчезнувшего, зависшего или некликабельного overlay. Если после него панели Battlegrounds остаются пустыми и в логе непрерывно идут `ScryInitializationException`, закрыть игру и HDT и выполнить чистый запуск общей записи **Hearthstone + Deck Tracker**.

## Запуск и порядок процессов

Для Battlegrounds предпочтительна только совместная запись Lutris. Launcher выполняет:

1. запуск Battle.net с `--exec="launch WTCG"`;
2. ожидание 12 секунд;
3. запуск HDT в том же Wine prefix.

Если перезапустить только HDT, пока Hearthstone уже находится в матче, Scry иногда не инициализируется и панели снова выглядят пустыми. В таком случае закрыть оба приложения и выполнить чистый запуск через **Hearthstone + Deck Tracker**. Несколько единичных ошибок Scry в начале допустимы, непрерывный поток `ScryInitializationException` — нет.

## Диагностика

### Процессы

```bash
pgrep -a -f '^C:.*Hearthstone Deck Tracker.exe$|^C:.*Hearthstone.exe -launch'
```

### Геометрия окон Hyprland

```bash
hyprctl clients -j | jq \
  '.[] | select(.title == "Hearthstone" or .title == "HearthstoneOverlay" or .title == "Hearthstone Deck Tracker") | {title, class, workspace: .workspace.id, at, size, floating, fullscreen, fullscreenClient}'
```

Оба окна должны находиться на workspace 5. Для текущей конфигурации ожидается:

```text
Hearthstone:        at [11,50], size [2730,1091]
HearthstoneOverlay: at [10,49], size [2729,1090]
HDT main window:    at [138,58], size [960,540]
```

У всех трёх окон `fullscreen` и `fullscreenClient` должны быть `0`. Hearthstone и overlay находятся на workspace 5, главное окно HDT — на workspace 3. Значения вроде overlay `[0,0] 666×457` означают внешний resize, а `[0,49] 4264×1161` — возврат Wine-бага.

После ручного изменения правил:

```bash
hyprctl reload
```

### Лог HDT

```bash
LOG='/home/mike/Games/hs/battlenet/drive_c/users/steamuser/AppData/Roaming/HearthstoneDeckTracker/Logs/hdt_log.txt'
tail -n 250 "$LOG"
rg -n 'HDT_WINE_FIXED_OVERLAY|BACON|Power|SnapshotCurrentBoard|BobsBuddy|ScryInitialization|ScryMemoryAccess|RuntimeBinder' "$LOG" | tail -n 120
```

Признаки рабочей Battlegrounds-интеграции:

```text
GameV2.CurrentMode >> BACON/GAMEPLAY
LogWatcherManager.OnLogFileFound >> Power
BattlegroundsBoardState.SnapshotCurrentBoard
BobsBuddyInvoker...
HDT_WINE_FIXED_OVERLAY_2730X1091: locking overlay to 3453,62 3412x1363
```

Единичные `ScryMemoryAccess`/`RuntimeBinder` при старте могут исчезнуть после инициализации. Непрерывные `ScryInitializationException` означают проблему порядка запуска, архитектуры или неполного дерева зависимостей.

### Если overlay снова чёрный

1. Выполнить `hdt-prelaunch.py --status`; transparency fix и layout должны быть `yes`.
2. Убедиться, что правило `HearthstoneOverlay` содержит `no_blur = true` и `opaque = false`.
3. Выполнить `hyprctl reload`.
4. Полностью закрыть и заново запустить связку через Lutris.
5. Если layout стал `no`, новый выпуск изменил реализацию кисти; не патчить произвольные байты, вернуть snapshot и переносить исправление на исходники новой версии.

### Если чёрный прямоугольник появляется на карте или в Choose One

1. Выполнить `hdt-prelaunch.py --status`; строка `Wine window opacity-mask disabled` должна быть `yes`.
2. Если там `no`, не продолжать игру на этом exe: обычный pre-launch должен вернуть последний совместимый snapshot.
3. Если marker есть, перезапустить только overlay через пункт Rofi **«Перезапустить HS Overlay»**.
4. Если дефект появился после нового официального тега, применить `local-opacity-mask.patch` к его исходникам и пересобрать custom exe. Изменение только `CardTooltip.xaml` этот дефект не исправляет.
5. Для подтверждения причины сверить форму: один прямоугольник при hover создаёт `SetCardOpacityMask`, несколько одинаковых прямоугольников над вариантами — `SetDiscoverCardOpacityMask`.

### Если панели Battlegrounds пустые

1. Проверить, что exe и Scry DLL обе x86-64 командой `file` выше.
2. Найти непрерывные Scry-ошибки в логе.
3. Закрыть и HDT, и Hearthstone; выполнить совместный запуск.
4. Если это началось сразу после обновления, вернуть датированный snapshot. Не заменять только одну DLL.

### Если правая панель снова не кликается

1. Проверить `Wine button fix: yes`.
2. Если `no`, обычный запуск guard должен автоматически восстановить snapshot.
3. Если `yes`, но новые элементы не кликаются, официальный UI добавил новые WPF-кнопки вне охвата PR #4741. Их нужно переносить на `OverlayButton` по аналогии с source-патчем.
4. Не лечить это глобальным `allows_input` для полноэкранного overlay: это перехватит клики у игры.

### Если центрально-левая область снова забирает курсор

1. Проверить `Wine Battlegrounds click-through zone: yes` в `hdt-prelaunch.py --status`.
2. Если marker отсутствует, обычный pre-launch должен вернуть рабочий snapshot.
3. Если monitor scale или разрешение менялись, пересчитать `WineBattlegroundsClickthroughRegion` в WPF/Win32-координатах и пересобрать exe.
4. Не расширять зону на левую session-панель, верхний Bob's Buddy или правые Guides/Minions: эти элементы должны оставаться интерактивными.

### Если preview снова справа или hover тормозит

Это означает, что новый выпуск прошёл критические проверки, но не содержит локальный патч. Временно вернуть manual snapshot либо применить `local-hover-preview.patch` к соответствующему тегу и пересобрать HDT.

### Если Bob's Buddy или нижние счётчики снова уехали вправо

1. Проверить `fixed overlay geometry: yes` в статусе.
2. Сверить обе геометрии через `hyprctl clients -j` с ожидаемыми значениями выше.
3. Найти в логе строку `HDT_WINE_FIXED_OVERLAY_2730X1091`.
4. Если marker отсутствует, обычный pre-launch должен вернуть snapshot; затем выполнить чистый совместный запуск.
5. Если marker есть, но текущий monitor scale/layout был изменён, пересчитать физические Win32/X11-константы и пересобрать exe.

### Если fullscreen/resize снова скрыл или сдвинул tracker

1. Проверить, что geometry guard запущен:

   ```bash
   pgrep -af '^python3 /home/mike/.config/waybar/scripts/wine-taskbar-icons.py$'
   ```

2. Снять состояние трёх окон командой из раздела «Геометрия окон Hyprland». Через одну секунду оно должно совпасть с эталоном и иметь оба fullscreen-state `0`.
3. Если процесса нет, запустить `setsid -f ~/.config/waybar/scripts/wine-taskbar-icons.py`.
4. Проверить `hyprctl configerrors`: вывод должен быть пустым.
5. Сверить активный скрипт с `config/wine-taskbar-icons.py`, а правила и guarded `Super+F` — с `config/hyprland-hdt.conf`; затем выполнить `hyprctl reload`.
6. Не заменять guard настоящим fullscreen: при текущем scale он неизбежно кладёт Hearthstone поверх overlay и меняет систему координат.

### Если Battle.net открылся не на workspace Lutris

Снять состояние окон:

```bash
hyprctl clients -j | jq -r \
  '.[] | select((.title|test("Battle.net|Lutris|Hearthstone";"i")) or (.class|test("battle|lutris|hearthstone";"i"))) | [.title,.class,.workspace.name,.pid] | @tsv'
```

При запущенном Lutris его workspace и workspace Battle.net должны совпасть не позднее чем через секунду. Без Lutris ожидается workspace 3. Hearthstone во всех случаях должен оставаться на workspace 5.

Если синхронизации нет:

1. проверить процесс `wine-taskbar-icons.py`;
2. сверить active script с `config/wine-taskbar-icons.py`;
3. проверить наличие rule `battlenet_workspace_fallback` из `config/hyprland-hdt.conf`;
4. выполнить `hyprctl reload` и убедиться, что `hyprctl configerrors` пуст.

### Если HDT не закрылся после Hearthstone

Подождать не менее 8 секунд и проверить журнал:

```bash
cat "$XDG_RUNTIME_DIR/hdt-autoclose.log"
```

Нормальная последовательность:

```text
Hearthstone observed; auto-close armed
Hearthstone stopped; HDT close grace period started
Requesting clean HDT shutdown via WM_CLOSE
HDT is no longer running; lifecycle state reset
```

Если первой строки нет, guard не видел текущую игровую сессию: проверить процесс guard и точный заголовок/процесс Hearthstone. Если есть запрос закрытия, но HDT сворачивается в tray, вернуть `<CloseToTray>false</CloseToTray>` в `config.xml`; при следующем запуске pre-launch guard сохранит остальные рабочие настройки как обычно. Резервный `SIGTERM` появится в журнале только через 15 секунд после неудачного `WM_CLOSE`.

### Если Lutris снова пишет, что executable не задан

Сначала проверить, какой корень выбрала текущая версия Lutris:

```bash
python - <<'PY'
from lutris import settings
print(settings.CONFIG_DIR)
PY
```

Для текущей установки ожидается `/home/mike/.local/share/lutris`. Затем проверить файлы и ссылки из YAML:

```bash
test ! -e /home/mike/.config/lutris
test -x /home/mike/.local/share/lutris/scripts/hdt-prelaunch.py
grep -R 'prelaunch_command\|exe:' /home/mike/.local/share/lutris/games/hearthstone*tracker*.yml
```

Если первый `test` не проходит, полностью закрыть Lutris и выяснить, что создало `~/.config/lutris`. Нельзя удалять каталог вслепую, если в нём уже появились реальные `games/*.yml`; сначала объединить конфиги с `~/.local/share/lutris`. Для этой задокументированной установки эталонными остаются YAML из `config/`, а активным единым корнем — `~/.local/share/lutris`.

### Если Waybar снова показывает вопросик или лишнюю иконку Wine

Проверить процесс и классы:

```bash
pgrep -af '^python3 /home/mike/.config/waybar/scripts/wine-taskbar-icons.py$'
hyprctl clients -j | jq -r \
  '.[] | select(.title == "Hearthstone" or .title == "Hearthstone Deck Tracker") | [.title,.class,.initialClass] | @tsv'
```

Ожидаемые текущие классы — `hearthstone-hand-drawn` и `hearthstone-deck-tracker`; `initialClass` может оставаться `steam_app_default`. Если процесса нет, запустить скрипт вручную и перезагрузить панель:

```bash
setsid -f ~/.config/waybar/scripts/wine-taskbar-icons.py
killall -SIGUSR2 waybar
```

Если у HDT появилась вторая иконка, проверить пустой helper:

```bash
for id in $(xdotool search --class '^steam_app_default$'); do
  title=$(xdotool getwindowname "$id" 2>/dev/null || true)
  geometry=$(xdotool getwindowgeometry --shell "$id" 2>/dev/null || true)
  if [ -z "$title" ] && grep -q '^WIDTH=160$' <<<"$geometry" && grep -q '^HEIGHT=20$' <<<"$geometry"; then
    xprop -id "$id" _NET_WM_STATE
  fi
done
```

У рабочего helper должен присутствовать `_NET_WM_STATE_SKIP_TASKBAR`. Если его нет, сверить активный скрипт с `config/wine-taskbar-icons.py` и перезапустить его.

## Откат

### Автоматический откат несовместимого обновления

Ничего вручную делать не нужно. При следующем запуске guard:

- копирует кандидат целиком в `~/.local/share/lutris/backups/hdt-overlay/rejected-updates/<sha256>/`;
- атомарно возвращает `working-current-wine`;
- выключает дальнейшие автоматические обновления.

После этого проверить `--status` и выполнить чистый совместный запуск.

### Ручной откат к сохранённому перед обновлением snapshot

Сначала полностью закрыть Wine-процессы. В переменной `GOOD` указать существующий датированный каталог, созданный перед обновлением:

```bash
HDT_DIR='/home/mike/Games/hs/battlenet/drive_c/users/steamuser/AppData/Local/HearthstoneDeckTracker/Hearthstone Deck Tracker'
BACKUP_ROOT="$HOME/.local/share/lutris/backups/hdt-overlay"
GOOD="$BACKUP_ROOT/manual-before-update-YYYYMMDD-HHMMSS"
STAMP="$(date +%Y%m%d-%H%M%S)"

test -f "$GOOD/Hearthstone Deck Tracker.exe"
mv "$HDT_DIR" "$HDT_DIR.after-update-$STAMP"
cp -a --reflink=auto "$GOOD" "$HDT_DIR"
mv "$BACKUP_ROOT/working-current-wine" \
  "$BACKUP_ROOT/working-current-wine.after-update-$STAMP"
cp -a --reflink=auto "$GOOD" "$BACKUP_ROOT/working-current-wine"

~/.local/share/lutris/scripts/hdt-prelaunch.py --disable-updates
~/.local/share/lutris/scripts/hdt-prelaunch.py --status
```

Команды сохраняют неудачную новую установку рядом, а не удаляют её. Если `test` завершился ошибкой, дальнейшие команды не выполнять и сначала исправить путь `GOOD`.

### Архив состояния до исправления Battlegrounds

Архив `hdt-before-bg-fix-20260710-1136.tar.zst` предназначен для аварийного разбора, а не для безусловного восстановления поверх рабочей установки. Сначала распаковать его отдельно:

```bash
mkdir -p /tmp/hdt-before-bg-fix
tar --zstd -xf \
  /home/mike/.local/share/lutris/backups/hdt-before-bg-fix-20260710-1136.tar.zst \
  -C /tmp/hdt-before-bg-fix
```

## Перенос исправлений на исходники

### Точное воспроизведение текущей функциональной версии

```bash
git clone https://github.com/HearthSim/Hearthstone-Deck-Tracker.git
cd Hearthstone-Deck-Tracker
git checkout 9e92f445f22d04f02c179c5cf6060f220dfe8929
git apply --check /home/mike/projects/deck-tracker-fix/hdt-wine-functional.patch
git apply /home/mike/projects/deck-tracker-fix/hdt-wine-functional.patch
git diff --check
```

Единый патч включает PR #4741, hover-оптимизацию, preview слева, фиксированную геометрию overlay, отключение несовместимой оконной opacity mask, постоянную центрально-левую click-through-зону и историю последних 20 игр с финальными билдами. Текущий `hdt-wine-functional.patch` рассчитан на базу v1.55.3; для старых сборок сохранены версионные патчи v1.55.1, v1.55.0, v1.54.2 и v1.53.6.

### Новый официальный тег

Сначала проверить, включён ли уже `OverlayButton` в новый выпуск.

Если Wine-фикс кнопок ещё не вошёл в тег:

```bash
git checkout <new-tag>
git am --3way /home/mike/projects/deck-tracker-fix/upstream-pr-4741.patch
git apply --3way /home/mike/projects/deck-tracker-fix/local-hover-preview.patch
git apply --3way /home/mike/projects/deck-tracker-fix/local-fixed-overlay-position.patch
git apply --3way /home/mike/projects/deck-tracker-fix/local-opacity-mask.patch
git apply --3way /home/mike/projects/deck-tracker-fix/local-clickthrough-zone.patch
git apply --3way /home/mike/projects/deck-tracker-fix/local-recent-games.patch
git diff --check
```

Если `OverlayButton` уже есть в официальном теге, не применять PR второй раз:

```bash
git checkout <new-tag>
git apply --3way /home/mike/projects/deck-tracker-fix/local-hover-preview.patch
git apply --3way /home/mike/projects/deck-tracker-fix/local-fixed-overlay-position.patch
git apply --3way /home/mike/projects/deck-tracker-fix/local-opacity-mask.patch
git apply --3way /home/mike/projects/deck-tracker-fix/local-clickthrough-zone.patch
git apply --3way /home/mike/projects/deck-tracker-fix/local-recent-games.patch
git diff --check
```

Конфликты на новом теге разрешать по смыслу. Особенно проверить семь локальных файлов:

```text
Hearthstone Deck Tracker/Controls/AnimatedCard.xaml.cs
Hearthstone Deck Tracker/Controls/AnimatedCardList.xaml.cs
Hearthstone Deck Tracker/Controls/Overlay/Battlegrounds/Minions/BattlegroundsCardsGroup.xaml
Hearthstone Deck Tracker/Controls/Tooltips/CardTooltip.xaml
Hearthstone Deck Tracker/Utility/Overlay/OverlayOpacityMask.cs
Hearthstone Deck Tracker/Windows/OverlayWindow.MouseOverDetection.cs
Hearthstone Deck Tracker/Windows/OverlayWindow.Update.cs
```

После переноса найти новые обычные `Button` в Battlegrounds overlay и прогнать тесты из `HDTTests/Battlegrounds/GuidesTabsOverlayCompatibilityTest.cs`.

## Примечания по сборке

Текущая сборка была получена под Wine с Windows .NET SDK 8.0.100 и .NET Framework 4.7.2 reference assemblies. После системного обновления Windows SDK под Wine запускается с `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1`, иначе несовпадение системной ICU и Wine останавливает `dotnet.exe` до MSBuild. NuGet assets восстанавливаются нативным Linux SDK с `--runtime win7-x64`, затем Windows-сборка выполняется с `--no-restore`: Wine не принимает просроченные подписи исторических NuGet-пакетов. Библиотеки взяты из полного официального архива v1.55.3. Localization зафиксирован на коммите `9a4e3f59ed090a6584349738e321834ca7d25f9b`; `Strings.Designer.cs` сгенерирован отдельным build-only инструментом. Для preserialized ресурсов временно использовался `System.Resources.Extensions`; изменение `.csproj` после сборки полностью отменено.

В рабочее дерево вместе с exe входят обязательные runtime-файлы:

```text
System.Buffers.dll
System.Memory.dll
System.Numerics.Vectors.dll
System.Resources.Extensions.dll
System.Runtime.CompilerServices.Unsafe.dll
```

Критически важные условия:

- собирать `Release x64`;
- использовать зависимости ровно того же выпуска, что и исходники;
- `AssemblyVersion` и `FileVersion` должны точно совпадать с полным номером из официального exe того же release — для v1.55.3 это `1.55.3.7390`, а не сокращённое `1.55.3`. Иначе скомпилированные WPF pack URI будут ссылаться на другую assembly и приложение упадёт до создания окна overlay;
- не переносить временные build-workaround изменения `.csproj` как продуктовый фикс;
- предпочтительно собирать на Windows/VM с полноценным MSBuild/Visual Studio, где старые генераторы ресурсов поддерживаются штатно.

После сборки новой версии:

1. Сделать отдельную копию текущего `working-current-wine`.
2. Установить полное официальное дерево нового выпуска одной архитектуры.
3. Заменить только exe на custom build, собранный из того же тега и против тех же DLL.
4. Запустить активный `hdt-prelaunch.py` без параметров: он проверит все пять marker, runtime-файлы, архитектуру, применит transparency patch и обновит snapshot.
5. Проверить `--status`, строку fixed-geometry в логе и все десять пунктов Battlegrounds-теста.

## Восстановление служебных конфигураций

Активный guard и вложенная копия должны совпадать по SHA-256. Если активный скрипт потерян:

```bash
install -Dm755 \
  /home/mike/projects/deck-tracker-fix/hdt-prelaunch.py \
  /home/mike/.local/share/lutris/scripts/hdt-prelaunch.py
```

Снимки Lutris и launcher лежат в `config/`. Их лучше использовать для сравнения, а не слепо перезаписывать после обновления Lutris: YAML может получить новые поля runner. Обязательные значения для обеих записей:

```yaml
system:
  prelaunch_command: /home/mike/.local/share/lutris/scripts/hdt-prelaunch.py
  prelaunch_wait: true
```

Guard намеренно хранится в `~/.local/share/lutris/scripts`, а не в `~/.config/lutris/scripts`: создание второго пути меняет выбранный Lutris корень и может снова скрыть все игровые YAML.

Совместная запись запускает:

```text
/home/mike/Games/hs/battlenet/drive_c/hdt-hearthstone-launcher.bat
```

Правила из `config/hyprland-hdt.conf` являются справочной выдержкой. Активные Lua-правила находятся в `~/.config/hypr/user/window_rules.lua`, общие cursor/render-настройки — в `~/.config/hypr/user/settings.lua`; синхронизированные source-копии хранятся под `~/projects/dotfiles/home/.config/hypr/user/`. После восстановления выполнить `hyprctl reload`.

Восстановление class/icon и geometry guard вместе с desktop entries:

```bash
install -Dm755 \
  /home/mike/projects/deck-tracker-fix/config/wine-taskbar-icons.py \
  /home/mike/.config/waybar/scripts/wine-taskbar-icons.py
install -Dm644 \
  /home/mike/projects/deck-tracker-fix/config/hearthstone.desktop \
  /home/mike/.local/share/applications/hearthstone.desktop
install -Dm644 \
  /home/mike/projects/deck-tracker-fix/config/hearthstone-deck-tracker.desktop \
  /home/mike/.local/share/applications/hearthstone-deck-tracker.desktop
install -Dm755 \
  /home/mike/projects/deck-tracker-fix/config/restart-hs-overlay \
  /home/mike/.local/bin/restart-hs-overlay
install -Dm644 \
  /home/mike/projects/deck-tracker-fix/config/restart-hs-overlay.desktop \
  /home/mike/.local/share/applications/restart-hs-overlay.desktop
update-desktop-database "$HOME/.local/share/applications"
```

В `~/.config/hypr/userprefs.conf` должна присутствовать строка:

```ini
exec-once = sh -c '"$HOME/.config/waybar/scripts/wine-taskbar-icons.py"'
unbind = $mainMod, F
bindd = $mainMod, F, Safe fullscreen (protect HDT overlay), exec, sh -c '"$HOME/.config/waybar/scripts/wine-taskbar-icons.py" --toggle-fullscreen'
```

Полные overlay/game/main-window rules, включая размеры и блокировку fullscreen, брать из `config/hyprland-hdt.conf`, а не восстанавливать частично. После установки выполнить `hyprctl reload` и убедиться, что `hyprctl configerrors` ничего не выводит.

В правиле `hearthstone_no_inactive_tint` класс должен учитывать уже переименованное окно:

```ini
match:class = ^(steam_app_default|hearthstone|hearthstone-hand-drawn)$
```

Если сами PNG были удалены, пересоздать их из установленного HDT и темы Tela:

```bash
HDT_ICO='/home/mike/Games/hs/battlenet/drive_c/users/steamuser/AppData/Local/HearthstoneDeckTracker/Hearthstone Deck Tracker/Images/HearthstoneDeckTracker.ico'
HS_MASTER='/home/mike/projects/deck-tracker-fix/assets/hearthstone-waybar.png'

for size in 16 22 24 32 48 64 128 256 512; do
  mkdir -p "$HOME/.local/share/icons/hicolor/${size}x${size}/apps"
done
magick "${HDT_ICO}[0]" -strip "$HOME/.local/share/icons/hicolor/16x16/apps/hearthstone-deck-tracker.png"
magick "${HDT_ICO}[1]" -strip "$HOME/.local/share/icons/hicolor/32x32/apps/hearthstone-deck-tracker.png"
magick "${HDT_ICO}[2]" -strip "$HOME/.local/share/icons/hicolor/48x48/apps/hearthstone-deck-tracker.png"
magick "${HDT_ICO}[3]" -resize 128x128 -strip "$HOME/.local/share/icons/hicolor/128x128/apps/hearthstone-deck-tracker.png"
magick "${HDT_ICO}[3]" -strip "$HOME/.local/share/icons/hicolor/256x256/apps/hearthstone-deck-tracker.png"
for size in 16 22 24 32 48 64 128 256 512; do
  magick "$HS_MASTER" -filter Lanczos -resize "${size}x${size}" -strip \
    "$HOME/.local/share/icons/hicolor/${size}x${size}/apps/hearthstone-hand-drawn.png"
done
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor"
update-desktop-database "$HOME/.local/share/applications"
hyprctl reload
killall -SIGUSR2 waybar
```

В `hearthstone.desktop` должны оставаться `Icon=hearthstone-hand-drawn` и `StartupWMClass=hearthstone-hand-drawn`. Уже установленные PNG не нужно пересоздавать после каждого обновления HDT.

## Контроль целостности

Проверить сам набор:

```bash
cd /home/mike/projects/deck-tracker-fix
sha256sum -c SHA256SUMS
```

В `SHA256SUMS` локальные файлы набора записаны относительными путями. Отдельный раздел в конце файла содержит комментарии с ожидаемыми хэшами установленного exe, snapshot и активного guard; их следует сверять командами из этой инструкции, потому что после контролируемого обновления они закономерно изменятся.

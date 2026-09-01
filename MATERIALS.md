# Материалы проекта Deck Tracker Fix

Актуальное состояние зафиксировано 19 августа 2026 года после обновления до
HDT v1.56.1 с сохранением исправлений Comp Guides и lifecycle overlay.
Чат намеренно не исправлен; в рабочую сборку не входят широкая
нижняя click-through-зона, принудительный возврат фокуса, X11 RECORD-listener,
`no_follow_mouse` и `cursor:no_warps`.

## Быстрая карта каталога

- `README.md` — полная эксплуатационная инструкция, диагностика, обновление и
  восстановление.
- `PATCH-MANIFEST.txt` — краткий состав функциональных изменений сборки.
- `SHA256SUMS` — контроль целостности всего переносимого комплекта.
- `hdt-wine-functional.patch` — единый патч для чистого upstream v1.56.1.
- `hdt-wine-functional-v1.56.1.patch` — его версионная копия.
- `hdt-wine-functional-v1.55.6.patch` — историческая копия прошлого патча.
- `hdt-wine-functional-v1.55.3.patch` — историческая копия прошлого патча.
- `local-*.patch` — отдельные локальные изменения для разбора и переноса на
  следующую версию.
- `upstream-pr-4741.patch` — исходный Wine-фикс интерактивных кнопок.
- `config/` — точные копии launcher, guard, Rofi, desktop- и Lutris-файлов,
  а также переносимый список proxy-доменов Nikki для сервисов HDT.
- Pre-launch guard закрепляет software rendering HDT, а window guard после
  трёхсекундной паузы автоматически поднимает только tracker, если его процесс
  исчез во время продолжающейся сессии Hearthstone.
- `assets/` — исходная иконка Hearthstone для Waybar.
- `local-recent-games.patch` — история последних 20 игр, кнопка раскрытия и
  тесты сохранения старых матчей.
- `artifacts/hdt-working-v1.56.1-recent-games.tar.zst` — текущий полный
  автономный снимок рабочего каталога HDT, включая exe, DLL, ресурсы и PDB.
- `artifacts/hdt-working-v1.56.1-recent-games.contents.sha256` — хэши всех 168
  файлов внутри текущего рабочего снимка.
- `artifacts/hdt-working-v1.55.6-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.55.3-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии с расширенной историей игр.
- `artifacts/hdt-working-v1.55.3-pre-chat.tar.zst` — исторический снимок до
  экспериментов с чатом и до расширенной истории игр.

## Зафиксированная версия

```text
HDT:                 1.56.1.7425
Upstream tag:        v1.56.1
Upstream commit:     00400dbfaf04e6e137893cabf0cb0ad1a4af4d47
Patched executable:  1dd610ac626a621d629d775bea21e3df08e89381478d16127b4d234db18bf7b9
Archive SHA-256:     73f0f73336341202cd81e7845a9f7ab8f615e2eeaa1bff65d4e27eee49439765
Contents manifest:   cccc7f0a5ecd2d3cf558dfe0b7dbf641be59335a6b894d6bb496dc240fd069a7
```

Рабочий exe содержит все проверяемые guard-маркеры: Wine-кнопки,
фиксированную геометрию, tooltip без нулевого состояния, отключённую
window-level opacity mask и центрально-левую Battlegrounds click-through-зону.
Панель `Latest Games` дополнительно раскрывает 20 последних матчей с финальными
билдами и сохраняет минимум 20 записей независимо от их возраста.
Неожиданное закрытие долгоживущего окна overlay теперь отменяется до штатного
`Core.Shutdown`, а ошибки Comp Guides переводят панель в повторяемое состояние
`Error`, не выходят из `async void` и не оставляют интерфейс навечно пустым.
Маршрутизация `hsreplay.net`, `hearthstonejson.com` и `hsdecktracker.net` через
Nikki `PROXY` воспроизводится из `config/nikki-hdt-proxy-domains.list`.

## Проверка комплекта

Из корня этого каталога:

```bash
sha256sum -c SHA256SUMS
tar --zstd -tf artifacts/hdt-working-v1.56.1-recent-games.tar.zst >/dev/null
```

Для глубокой проверки содержимого архива:

```bash
tmp="$(mktemp -d)"
tar --zstd -xf artifacts/hdt-working-v1.56.1-recent-games.tar.zst -C "$tmp"
(cd "$tmp" && sha256sum -c \
  /home/mike/projects/deck-tracker-fix/artifacts/hdt-working-v1.56.1-recent-games.contents.sha256)
rm -rf "$tmp"
```

## Автономное восстановление

Выполнять при полностью закрытом HDT. Hearthstone рекомендуется тоже закрыть,
если восстанавливается вся установка, а не только overlay между матчами.

```bash
project=/home/mike/projects/deck-tracker-fix
install='/home/mike/Games/hs/battlenet/drive_c/users/steamuser/AppData/Local/HearthstoneDeckTracker/Hearthstone Deck Tracker'
snapshot='/home/mike/.local/share/lutris/backups/hdt-overlay/working-current-wine'
tmp="$(mktemp -d)"

tar --zstd -xf "$project/artifacts/hdt-working-v1.56.1-recent-games.tar.zst" -C "$tmp"
rsync -a --delete "$tmp/" "$install/"
rsync -a --delete "$tmp/" "$snapshot/"
rm -rf "$tmp"

~/.local/share/lutris/scripts/hdt-prelaunch.py --status
```

После этого запускать единственную запись Lutris **Hearthstone + Deck Tracker**.
Для перезапуска только overlay во время уже запущенной игры использовать пункт
Rofi **«Перезапустить HS Overlay»**.

## Перенос на новую версию

1. Прочитать раздел «Обновление HDT» в `README.md` и сделать датированную
   резервную копию текущей установки.
2. Взять исходники точного нового тега HDT.
3. Перенести `hdt-wine-functional.patch` по смыслу; не копировать старый exe в
   каталог с DLL другой версии.
4. Не возвращать изменения для Battle.net-чата, перечисленные в начале файла.
5. Собрать x86-64 exe, проверить все guard-маркеры и только затем заменить весь
   официальный каталог одной версии.
6. После живой проверки обновить архив, manifest, README и `SHA256SUMS`.

Исходный рабочий каталог на этой машине:

```text
/home/mike/projects/Hearthstone-Deck-Tracker-v1.56.1
```

Переносимым источником истины являются патчи и архив в этом проекте: исходный
worktree может содержать build-артефакты и не требуется для восстановления.

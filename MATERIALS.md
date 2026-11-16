# Материалы проекта Deck Tracker Fix

Актуальное состояние зафиксировано 4 ноября 2026 года после сборки HDT v1.59.8.9020 из точного коммита выпуска с локальными Wine-фиксами.
Чат намеренно не исправлен; в рабочую сборку не входят широкая
нижняя click-through-зона, принудительный возврат фокуса, X11 RECORD-listener,
`no_follow_mouse` и `cursor:no_warps`.

## Быстрая карта каталога

- `README.md` — полная эксплуатационная инструкция, диагностика, обновление и
  восстановление.
- `PATCH-MANIFEST.txt` — краткий состав функциональных изменений сборки.
- `SHA256SUMS` — контроль целостности всего переносимого комплекта.
- `hdt-wine-functional.patch` — все локальные исправления для коммита v1.59.8 `2698623d`.
- `hdt-wine-functional-v1.59.8.patch` — версионная копия текущего патча.
- `build-v1.59.8/` — описание сборки и результаты проверок.
- `hdt-wine-functional-v1.59.3-donor.patch` — исторический патч донора v1.59.3.
- `binary-fix-v1.59.3/` — инструменты переноса в официальный exe и аудит проверок.
- `hdt-wine-functional-v1.58.9.patch` — исторический source-патч v1.58.9.
- `build-v1.58.9/` — исторические результаты проверок v1.58.9.
- `hdt-wine-functional-v1.58.6-donor.patch` — версионная копия патча донора.
- `binary-fix-v1.58.6/` — инструменты переноса, инструкция и результаты проверок.
- `hdt-wine-functional-v1.58.5.patch` — исторический source-патч v1.58.5.
- `hdt-wine-functional-v1.58.2.patch` — историческая копия предыдущего патча.
- `hdt-wine-functional-v1.58.0.patch` — историческая копия прошлого патча
  (база `8f8e499c`).
- `hdt-wine-functional-v1.57.12.patch` — историческая копия прошлого патча
  (база `bb3493f2`).
- `hdt-wine-functional-v1.57.10.patch` — историческая копия прошлого патча
  (база `8cb074f6`).
- `hdt-wine-functional-v1.57.6.patch` — историческая копия прошлого патча
  (база `dbd9af96`).
- `hdt-wine-functional-v1.56.1.patch` — историческая копия прошлого патча
  (последняя, включающая PR #4741).
- `hdt-wine-functional-v1.55.6.patch` — историческая копия прошлого патча.
- `hdt-wine-functional-v1.55.3.patch` — историческая копия прошлого патча.
- `local-*.patch` — отдельные локальные изменения для разбора и переноса на
  следующую версию.
- `upstream-pr-4741.patch` — исходный Wine-фикс интерактивных кнопок; нужен
  только для тегов старше v1.57.0.
- `config/` — точные копии launcher, guard, Rofi, desktop- и Lutris-файлов,
  а также переносимый список proxy-доменов Nikki для сервисов HDT.
- Pre-launch guard закрепляет software rendering HDT, а window guard после
  трёхсекундной паузы автоматически поднимает только tracker, если его процесс
  исчез во время продолжающейся сессии Hearthstone.
- `assets/` — исходная иконка Hearthstone для Waybar.
- `local-recent-games.patch` — история последних 20 игр, кнопка раскрытия и
  тесты сохранения старых матчей.
- `artifacts/hdt-working-v1.59.8-recent-games.tar.zst` — текущий полный
  автономный снимок рабочего каталога HDT, включая exe, DLL и ресурсы.
- `artifacts/hdt-working-v1.59.8-recent-games.contents.sha256` — хэши всех 157
  файлов внутри текущего рабочего снимка.
- `artifacts/hdt-working-v1.59.3-recent-games.tar.zst` — предыдущий рабочий снимок.
- `artifacts/hdt-working-v1.58.9-recent-games.tar.zst` — исторический снимок.
- `artifacts/hdt-working-v1.58.6-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.58.5-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.58.2-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.58.0-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.57.12-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.57.10-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.57.6-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.56.1-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.55.6-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.55.3-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии с расширенной историей игр.
- `artifacts/hdt-working-v1.55.3-pre-chat.tar.zst` — исторический снимок до
  экспериментов с чатом и до расширенной истории игр.

Установлена HDT v1.59.8.9020 из опубликованного коммита выпуска с Wine-фиксами. Все 53 официальных DLL совпадают побайтно. Пройдены 15 тестов истории, кнопок и рейтинга.

## Зафиксированная версия

```text
HDT:                 1.59.8.9020
Upstream release:    v1.59.8 (HDT-Releases, 2026-11-03)
Upstream commit:     2698623dc0e91491671a614ae176f9db68831aa7
Localization commit: 7d7045c17c700ea24299732330da8a8e62fd8788
Patched executable:  46e5e17c3bc709da15baae36ecd544eefbb4aa665b38cbbf58b614a24897e07b
Built executable:    978699e18a6f972a9338562bee86e9f0f87c491aa634b48684c209092a07b432 (до transparency patch)
Archive SHA-256:     a273410503d367e337d35100a0dae1767a26cbc4d776cb13a450bb8e174a04be
Contents manifest:   1f493a0ccec575259fead5dc9b1ec97d1cee2070652026a20e8c6996835c2f7e
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
tar --zstd -tf artifacts/hdt-working-v1.59.8-recent-games.tar.zst >/dev/null
```

Для глубокой проверки содержимого архива:

```bash
tmp="$(mktemp -d)"
tar --zstd -xf artifacts/hdt-working-v1.59.8-recent-games.tar.zst -C "$tmp"
(cd "$tmp" && sha256sum -c \
  /home/mike/projects/deck-tracker-fix/artifacts/hdt-working-v1.59.8-recent-games.contents.sha256)
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

tar --zstd -xf "$project/artifacts/hdt-working-v1.59.8-recent-games.tar.zst" -C "$tmp"
rsync -a --delete "$tmp/" "$install/"
rsync -a --delete "$tmp/" "$snapshot/"
rm -rf "$tmp"

~/.local/share/lutris/scripts/hdt-prelaunch.py --status
```

После этого запускать единственную запись Lutris **Hearthstone + Deck Tracker**.
Для перезапуска только overlay во время уже запущенной игры использовать пункт
Rofi **«Перезапустить HS Overlay»**.

## Перенос на новую версию

Nomi's Kitchen v1.10.0 установлен отдельно от сборки HDT. Настройки сохранены
в `config/NomisKitchenHDT.config.json`, `config/nomis-plugins.xml` и
`config/nomis-doorstop.ini`; Wine override `winhttp: n,b` включён в
`config/hearthstone-plus-deck-tracker.yml`. Архив HDT не содержит установщик
плагина и игровые компоненты BepInEx. Их установка, резервная копия перед
обновлением и проверка описаны в разделах «Обновление HDT» и «Nomi's Kitchen»
в `README.md`.

Текущая v1.59.8 собрана из опубликованного коммита выпуска. Порядок описан в `build-v1.59.8/README.md`. Для выпусков без исходников сохранены инструменты бинарного переноса v1.59.3.


1. Прочитать раздел «Обновление HDT» в `README.md` и сделать датированную
   резервную копию текущей установки.
2. Взять исходники нового выпуска: номер — из HDT-Releases, базовый коммит —
   из `master` с сообщением `v<версия>` (тегов с 1.57.x нет), полный номер
   сборки — из официального exe в `-full.nupkg`.
3. Перенести `hdt-wine-functional.patch` (`git apply --3way`) по смыслу; не
   копировать старый exe в каталог с DLL другой версии. PR #4741 повторно не
   применять — он уже в upstream.
4. Не возвращать изменения для Battle.net-чата, перечисленные в начале файла.
5. Собрать x86-64 exe из точного коммита выпуска или перенести фиксы в официальный
   exe с проверкой методов и ресурсов. Проверить guard и тесты, затем заменить
   полный каталог одной версии.
6. После живой проверки обновить архив, manifest, README и `SHA256SUMS`.

Исходный рабочий каталог на этой машине:

```text
/home/mike/projects/Hearthstone-Deck-Tracker-v1.59.8   (detached HEAD 2698623d, локальный патч)
/home/mike/projects/Hearthstone-Deck-Tracker-v1.58.0   (предыдущая, ветка wine-fixes-v1.58.0)
```

Окружение сборки и журналы: `~/.cache/hdt-build/v1.59.8/` (`prep.sh`, `build.sh`,
`tests-build.sh`, `deploy.py`, `candidate-1.59.8.9020/`, `guard-test/`, `regression-tests.log`,
`deployed-backup-path.txt`).

Переносимым источником истины являются патчи и архив в этом проекте: исходный
worktree может содержать build-артефакты и не требуется для восстановления.

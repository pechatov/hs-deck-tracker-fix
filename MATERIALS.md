# Материалы проекта Deck Tracker Fix

Актуальное состояние зафиксировано 4 сентября 2026 года после обновления до
HDT v1.57.6 (upstream `master` `dbd9af96`, git-тегов для 1.57.x нет) с
переносом всех локальных исправлений. Wine-фикс кнопок PR #4741 теперь входит в
upstream и в локальный патч не включается.
Чат намеренно не исправлен; в рабочую сборку не входят широкая
нижняя click-through-зона, принудительный возврат фокуса, X11 RECORD-listener,
`no_follow_mouse` и `cursor:no_warps`.

## Быстрая карта каталога

- `README.md` — полная эксплуатационная инструкция, диагностика, обновление и
  восстановление.
- `PATCH-MANIFEST.txt` — краткий состав функциональных изменений сборки.
- `SHA256SUMS` — контроль целостности всего переносимого комплекта.
- `hdt-wine-functional.patch` — единый патч для чистого upstream v1.57.6
  (коммит `dbd9af96`), только локальные изменения.
- `hdt-wine-functional-v1.57.6.patch` — его версионная копия.
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
- `artifacts/hdt-working-v1.57.6-recent-games.tar.zst` — текущий полный
  автономный снимок рабочего каталога HDT, включая exe, DLL, ресурсы и PDB.
- `artifacts/hdt-working-v1.57.6-recent-games.contents.sha256` — хэши всех 175
  файлов внутри текущего рабочего снимка.
- `artifacts/hdt-working-v1.56.1-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.55.6-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии.
- `artifacts/hdt-working-v1.55.3-recent-games.tar.zst` — исторический снимок
  предыдущей рабочей версии с расширенной историей игр.
- `artifacts/hdt-working-v1.55.3-pre-chat.tar.zst` — исторический снимок до
  экспериментов с чатом и до расширенной истории игр.

## Зафиксированная версия

```text
HDT:                 1.57.6.8270
Upstream release:    v1.57.6 (HDT-Releases, 2026-09-03)
Upstream commit:     dbd9af96f68498dab72c67b3bf0267ae93012816 (master, без тега)
Localization commit: 073618e76c91da02e42a31cc5fd3afd08a5122b7
Patched executable:  d76cf0a7d6884cc5665a35eccb782ad62d03c1c5b65aed590f666d6515213a5a
Built executable:    4de74719da41ddba6528086b38741188371fd485b7bca77737ccb1f11f063f1d (до transparency patch)
Archive SHA-256:     23cf588e3c6941d6bb7c862aac134f9071876ee7185af02ee8f997ab779d932d
Contents manifest:   a5fc48b53aa7609c1156615ce9421294bd33187003f89b1a12013c1b46b0f4f8
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
tar --zstd -tf artifacts/hdt-working-v1.57.6-recent-games.tar.zst >/dev/null
```

Для глубокой проверки содержимого архива:

```bash
tmp="$(mktemp -d)"
tar --zstd -xf artifacts/hdt-working-v1.57.6-recent-games.tar.zst -C "$tmp"
(cd "$tmp" && sha256sum -c \
  /home/mike/projects/deck-tracker-fix/artifacts/hdt-working-v1.57.6-recent-games.contents.sha256)
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

tar --zstd -xf "$project/artifacts/hdt-working-v1.57.6-recent-games.tar.zst" -C "$tmp"
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
2. Взять исходники нового выпуска: номер — из HDT-Releases, базовый коммит —
   из `master` с сообщением `v<версия>` (тегов с 1.57.x нет), полный номер
   сборки — из официального exe в `-full.nupkg`.
3. Перенести `hdt-wine-functional.patch` (`git apply --3way`) по смыслу; не
   копировать старый exe в каталог с DLL другой версии. PR #4741 повторно не
   применять — он уже в upstream.
4. Не возвращать изменения для Battle.net-чата, перечисленные в начале файла.
5. Собрать x86-64 exe, проверить все guard-маркеры и только затем заменить весь
   официальный каталог одной версии.
6. После живой проверки обновить архив, manifest, README и `SHA256SUMS`.

Исходный рабочий каталог на этой машине:

```text
/home/mike/projects/Hearthstone-Deck-Tracker-v1.57.6   (ветка wine-fixes-v1.57.6)
/home/mike/projects/Hearthstone-Deck-Tracker-v1.56.1   (предыдущая, ветка wine-fixes-v1.56.1)
```

Окружение сборки и журналы: `~/.cache/hdt-build/v1.57.6/` (`build.log`,
`tests.log`, `candidate-1.57.6.8270/`, `deployed-backup-path.txt`).

Переносимым источником истины являются патчи и архив в этом проекте: исходный
worktree может содержать build-артефакты и не требуется для восстановления.

# Implementation Demo Video Script

Target length: 3 minutes 30 seconds to 3 minutes 50 seconds. Required format: MP4. Record the terminal window at a readable size and keep the command prompt and result text visible.

## Before recording

- Open PowerShell in the project root.
- Run `python -m src.main`.
- Use a clean session and the example values below.
- Keep personal information out of the demo data. The contact values below are fictional examples.

## Demonstration sequence

| Time | Action | What the viewer should see |
| --- | --- | --- |
| 0:00-0:15 | Show the project root and start `python -m src.main` | The `pim>` prompt and the local command-line system |
| 0:15-0:55 | Create one Plain Text listing, one Contact, one Task, and one Event | Four `OK: created PIR ...` results with IDs 1-4 |
| 0:55-1:25 | Search with `type = text && content contains "ipad"` | One matching listing and its details |
| 1:25-1:55 | Update PIR 1 so its content changes from `status: available` to `status: sold` | An `OK: updated PIR 1` result and the updated content |
| 1:55-2:25 | Run `print all` and then `delete 4` | Stable ID order, detailed records, and a delete confirmation |
| 2:25-2:55 | Save with `save campus_market.pim` | A successful save message and the local `.pim` filename |
| 2:55-3:25 | Exit, restart the program, and run `load campus_market.pim` followed by `print all` | The four saved records restored with their original IDs |
| 3:25-3:45 | Enter one invalid command or criterion | A readable `ERROR:` message while the program remains usable |

## Commands to paste

```text
create text content="title: iPad Air 5; category: electronics; condition: good; price: HKD 2000; status: available; description: Includes case"
create contact name="Chan Tai Man" address="Hung Hom" mobile="91234567"
create task description="Confirm payment" deadline="2026-11-20 18:00"
create event description="Campus handover" start="2026-11-21 14:00" alarm="2026-11-21 13:30"
search type = text && content contains "ipad"
update 1 content="title: iPad Air 5; category: electronics; condition: good; price: HKD 2000; status: sold; description: Includes case"
print all
delete 4
save campus_market.pim
exit
```

Start a second session and paste:

```text
load campus_market.pim
print all
exit
```

## Editing and delivery

Add the resulting MP4 as `recordings/system-demo.mp4`. Confirm that its duration is no more than four minutes and that the terminal text is legible. The course video requirement does not replace the separate presentation recording requirement.

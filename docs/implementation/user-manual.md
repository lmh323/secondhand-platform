# User Manual

## Start the program

Open PowerShell in the `secondhand-platform` project root and run:

```powershell
python -m src.main
```

The prompt is `pim>`. Text values containing spaces must be enclosed in double quotes.

## Create records

```text
create text content="title: iPad Air; category: electronics; condition: good; price: HKD 2000; status: available; description: Includes case"
create task description="Confirm payment" deadline="2026-11-20 18:00"
create event description="Campus handover" start="2026-11-21 14:00" alarm="2026-11-21 13:30"
create contact name="Chan Tai Man" address="Hung Hom" mobile="91234567"
```

The program assigns an integer ID to every new record and prints the created record.

## Search and inspect

```text
search type = text && content contains "ipad"
search description contains "payment" || name contains "Chan"
search deadline < "2026-11-20 20:00"
print 1
print all
```

Text searches ignore letter case. Search precedence is `!`, then `&&`, then `||`; parentheses can change the order.

## Update and delete

```text
update 1 content="title: iPad Air; status: sold"
update 2 deadline="2026-11-21 18:00"
delete 4
```

An update keeps the record ID and type. Invalid fields or values leave the record unchanged.

## Save and load

```text
save campus_market.pim
load campus_market.pim
```

Only paths ending in `.pim` are accepted. Loading a valid file replaces the current in-memory records. A failed load keeps the current records.

## Help and errors

Use `help` to display the command list. Successful operations begin with `OK:`, search output begins with `MATCHES:`, and invalid input begins with `ERROR:`. The program continues after recoverable errors.

## Example second-hand trade workflow

1. Create a Plain Text record for the item.
2. Create a Contact record for the buyer or seller.
3. Create a Task record for payment or preparation.
4. Create an Event record for inspection or campus handover.
5. Search for the item and update its listing text to `status: sold` after the exchange.
6. Save the repository to a `.pim` file.

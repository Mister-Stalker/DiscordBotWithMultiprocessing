# DiscordBotWithMultiprocessing
Bot for discord on python with multiprocessing. 
Бот для Discord на python с использованием multiprocessing

Этот проект является просто примером как можно использовать multiprocessing
для создания бота с командами, на выполнение которых необходимо много времени 
(много расчетов).

Для работы необходимо добавить в класс `discord.Interaction` 
поле source_data (в `__slots__`) и в метод `_from_data` 
дописать `self.source_data = data`.
Должно получиться примерно так:
```python
...
def _from_data(self, data: InteractionPayload):
    self.source_data = data
    
    self.id: int = int(data['id'])
    self.type: InteractionType = try_enum(InteractionType, data['type'])
    self.data: Optional[InteractionData] = data.get('data')
...
```
Аналогично нужно сделать с `discord.Message`.
Выглядит странно, но это необходимо для работы. 
Можно было реализовать передачу Interaction в другой процесс и по другому, 
но это было бы сложнее и менее стабильно.
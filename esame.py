class ExamException(Exception):
  pass


class CSVFile:

  def __init__(self, name=""):
    self.name = name

  def get_data(self):
    try:
      my_file = open(self.name, 'r')

    except Exception as e:
      raise ExamException('Errore {}'.format(e))

    list_values = []

    for line in my_file:
      elements = line.strip('\n').split(',')

      if elements[0] != 'epoch':
        list_values.append(elements)

    my_file.close()

    if not len(list_values):
      raise ExamException("Errore, lista vuota")

    return list_values


class CSVTimeSeriesFile(CSVFile):

  def get_data(self):
    list_elements = super().get_data()
    parsed_list = []

    for element in list_elements:

      #varaibile booleana utilizzata per inserire
      #un element nella parsed_list
      add_new = True

      new_row = []

      for index, column in enumerate(element):

        if index == 0:

          try:
            new_row.append(int(column))

          #se non riesco a converitre il timestamp a int
          #provo a convertirlo prima a floating point
          except:

            try:
              data = float(column)
              new_row.append(int(data))

            except:
              add_new = False
              break

        else:

          try:
            if len(new_row) < 2:
              new_row.append(float(column))

          except:
            add_new = False
            break

      if add_new is True:
        parsed_list.append(new_row)

    verified_list = self.verify_data(parsed_list)
    return verified_list

#metodo utilizzato per controllare che non siano presenti
#timestamp duplicati e che siano ordinati
  def verify_data(self, parsed_list):

    for i, hours in enumerate(parsed_list):

      for j, next_hours in enumerate(parsed_list):

        if i != j and hours[0] == next_hours[0]:
          raise ExamException("Errore, valore duplicato")

        if i < j and hours[0] > next_hours[0]:
          raise ExamException("Errore, lista disordinata")

    return parsed_list


#funzione che calcola la differenza massima per giorno
def compute_daily_max_difference(time_series):

  sanitized_time_series = check_input(time_series)

  #accumulatore di temperature divise per giorni
  list_temp_day = []

  #variabile utilizzata come indice di sanitized_time_series
  index = 0

  for current_epoch in sanitized_time_series:
    current_epoch = sanitized_time_series[index]
    temp_list = []
    day_start_epoch = current_epoch[0] - (current_epoch[0] % 86400)

    for next_epoch in sanitized_time_series:
      next_day_start_epoch = next_epoch[0] - (next_epoch[0] % 86400)

      if next_epoch[0] >= current_epoch[0]:
        if next_day_start_epoch == day_start_epoch:
          temp_list.append(next_epoch[1])
          index += 1

        else:
          break

    list_temp_day.append(temp_list)

    if index > len(sanitized_time_series) - 1:
      break

  list_max_difference_temp = []

  for temperature in list_temp_day:

    if len(temperature) > 1:
      max_difference = max(temperature) - min(temperature)
      list_max_difference_temp.append(max_difference)

    else:
      list_max_difference_temp.append(None)

  return list_max_difference_temp


#funzione che controlla l'input di compute_daily_max_difference
def check_input(check_list):

  time_series = []
  if not isinstance(check_list, list) or not len(check_list):
    raise ExamException("Errore, lista vuota")

  for row in check_list:

    if type(row) != list:
      continue

    if len(row) > 1:
      if len(row) == 0:
        continue

      if type(row[0]) != int:
        continue

      if type(row[1]) != float:
        continue

      else:
        time_series.append(row)

  if not len(time_series):
    raise ExamException("Errore, Lista vuota")

  return time_series


#esecuzione
time_series_file = CSVTimeSeriesFile(name='data.csv')
time_series = time_series_file.get_data()

for element in time_series:
  print(element)

lists = compute_daily_max_difference(time_series)
#lists=compute_daily_max_difference([[8,12.7],[None, 3.2],[2, 'x'], []])
print('Escursioni termiche')
i = 1

for element in lists:
  print("giorno numero_" + str(i) + " = " + str(element))
  i += 1
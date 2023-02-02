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
      elements = line.strip().split(',')

      if elements[0] != 'epoch':
        
        #voglio che la lista sia composta da due elementi
        #epoch e temperature
        if len(elements)>1:
          list_values.append(elements)

    my_file.close()

    if not len(list_values):
      raise ExamException("Errore, lista vuota")

    return list_values


class CSVTimeSeriesFile(CSVFile):

  def get_data(self):
    list_elements = super().get_data()
    
    #lista che conterrà i time_series ma in formato numerico    
    parsed_list = []

    #ciclo su tutte le righe del file
    for element in list_elements:

      #varaibile booleana utilizzata per inserire
      #un element nella parsed_list
      add_new = True
      
      #preparo una lista in cui verranno salvati i dati
      #di una riga ma in formato numerico
      new_row = []

      #ciclo su tutti gli elementi della riga
      for index, column in enumerate(element):

        if index == 0:

          #provo a convertire il primo elemento a intero
          try:
            new_row.append(int(column))

          #se non riesco a converitrlo
          #provo a convertirlo prima a floating point
          except:

            try:
              data = float(column)
              new_row.append(int(data))

            # se fallisce allora esco dal ciclo
            # e la variabile booleana viene messa a False
            except:
              add_new = False
              break

        else:

          # tutti gli elementi successivi al primo
          # vengono convertiti a floating point
          # se non riesco allora esco dal ciclo
          try:
            if len(new_row) < 2:
              new_row.append(float(column))

          except:
            add_new = False
            break

      
      if add_new is True:
        parsed_list.append(new_row)

    if not len(parsed_list):
      raise ExamException("Errore, lista vuota")
    
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

  #ciclo su tutti gli elementi della lista
  #trovo i timestamp appartenenti allo stesso giorno
  for current_epoch in sanitized_time_series:

    #mi sposto all'epoch che appartiene a un altro giorno
    current_epoch = sanitized_time_series[index]
    
    #lista in cui salvo le temperature appartenenti
    #allo stesso giorno
    temp_list = []
    day_start_epoch = current_epoch[0] - (current_epoch[0] % 86400)

    for next_epoch in sanitized_time_series:
      next_day_start_epoch = next_epoch[0] - (next_epoch[0] % 86400)

      if next_epoch[0] >= current_epoch[0]:

        #finchè i timestamp appartengono allo stesso giorno
        #aggiungo la temperatura alla lista
        #altrimenti esco dal ciclo 
        if next_day_start_epoch == day_start_epoch:
          temp_list.append(next_epoch[1])
          index += 1

        else:
          break

    list_temp_day.append(temp_list)
    
    #se l'indice è maggiore dell'indice massimo della lista
    #esco dal ciclo
    if index > len(sanitized_time_series) - 1:
      break

  #lista che conterrà le differenze massime di temperatura
  list_max_difference_temp = []

  #ciclo sulla lista che contiene
  #tutte le temperature divise per giorno
  for temperature in list_temp_day:

    #se la lunghezza della sottolista è minore o uguale a 1
    #allora aggiungo None 
    if len(temperature) > 1:
      max_difference = max(temperature) - min(temperature)
      list_max_difference_temp.append(max_difference)

    else:
      list_max_difference_temp.append(None)

  return list_max_difference_temp


#funzione che controlla e sanifica
#l'input di compute_daily_max_difference
def check_input(check_list):

  time_series = []

  #se l'input non è di tipo lista o la lunghezza è uguale a 0
  #alza l'eccezione
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
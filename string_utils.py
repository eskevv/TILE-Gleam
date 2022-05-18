class StringTurn:
   def iterate_with(self, text, string, iteration):
      for index in range(iteration, len(text)):
         for c in range(len(string)):
            if text[index + c] != string[c]:
               break
            if c == len(string) - 1:
               return index
      return -1

   def find_between(self, text, first, last = '', offset = 0, start = 0):
      """Gets the indexes of the first occurance of the first given string and the
      last occurance of the second given string."""

      first_index = self.iterate_with(text, first, start)
      if first_index != -1:
         second_index = self.iterate_with(text, last, first_index + len(first))
         if second_index != -1:
            return [first_index + offset, second_index + (len(last) - 1) - offset]
         return [first_index, -1]
      return [-1, -1]

   def string_within(self, text, first, last):
      indexes = self.find_between(text, first, last)
      start = indexes[0]
      finish = indexes[1] + 1
      if start != -1 and finish != -1:
         return text[start:finish]
      return None

   def string_inside(self, text = 'pull_from', ends = (0, 1)):
      start = ends[0]
      finish = ends[1] + 1
      return text[start:finish]

st = StringTurn()
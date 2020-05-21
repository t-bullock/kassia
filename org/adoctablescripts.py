import re
import sys

def find_pos_of_nth_substr(in_string, num, substr):
  pos=-1
  iter=0
  while(iter<num):
    pos=in_string.find(substr,pos+1)
    if(in_string[pos-1] != '\\'):
      iter+=1
  return(pos)


def adoc_table_to_orgtbl(in_string, delimiter):
  field_count  = 9
  in_string    = re.sub('\n',' ', in_string)
  table_begin  = in_string.find('|===',0)+4
  table_end    = in_string.find('|===',table_begin+1)
  in_string    = in_string[table_begin:table_end]
  out_string   = ''
  for f in range(384):
    index        = find_pos_of_nth_substr(
      in_string,
      field_count+1,
      delimiter)
    out_string += in_string[0:index] + '\n'
    in_string   = in_string[index:]
  return(out_string)


def get_column(in_string, column, delimiter):
  in_string  = adoc_table_to_orgtbl(in_string, delimiter).splitlines()
  out_string = ''
  for f in range(len(in_string)):
    cur_lin = in_string[f]
    beg_col = find_pos_of_nth_substr(cur_lin, column+1, delimiter)+1
    end_col = find_pos_of_nth_substr(cur_lin, column+2, delimiter)
    in_string[f] = cur_lin[beg_col:end_col]
    out_string += re.sub('\\\\\\' + delimiter, delimiter, in_string[f] + '\n')
  return(out_string.rstrip())


stdin = sys.stdin.read()
if len(sys.argv) < 2:
  print("Error: Missing args")

elif sys.argv[1] == "print-column" :
  if len(sys.argv) > 2:
    print(get_column(stdin, int(sys.argv[2]), '|'))
  else:
    print("Error: no column specified")

else:
  print("Error: First arg must be a command, ie 'print-column'")

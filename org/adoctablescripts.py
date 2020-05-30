import re
import sys

def is_escaped(in_string, char_pos):
    return( in_string[char_pos-1] == '\\'
            and not is_escaped(in_string, char_pos-1))


def find_nth_substr(in_string, num, substr):
    def inner_func(in_string, num, substr, pos, i):
        new_pos = in_string.find(substr, pos if pos==i==0 else pos+1)
        new_i   = i if is_escaped(in_string, pos) else i+1
        if i >= num and new_i != i or pos == -1:
            return pos
        return inner_func(in_string, num, substr, new_pos, new_i)
    return inner_func(in_string, num, substr, 0, 0)


def arrange_in_columns(in_string, delimiter, field_count):
    intermediate_string    = re.sub('\n',' ', in_string)
    table_begin            = intermediate_string.find('|===',0)+4
    table_end              = intermediate_string.find('|===',table_begin+1)
    intermediate_string    = intermediate_string[table_begin:table_end]
    out_string             = ''

    index = 0
    while index != -1:
        index = find_nth_substr(
            intermediate_string,
            field_count+1,
            delimiter)
        out_string += intermediate_string[0:index] + '\n'
        intermediate_string = intermediate_string[index:]

    return(out_string)


def get_column(in_string, column, delimiter, field_count):
    intermediate_string = arrange_in_columns(
            in_string,
            delimiter,
            field_count
            ).splitlines()
    out_string=''

    for f in range(len(intermediate_string)):
        cur_lin = intermediate_string[f]
        beg_col = find_nth_substr(cur_lin,
                                  column+1,
                                  delimiter)+1
        end_col = find_nth_substr(cur_lin,
                                  column+2,
                                  delimiter)
        intermediate_string[f] = cur_lin[beg_col:end_col]
        out_string += re.sub('\\\\\\' + delimiter,
                             delimiter,
                             intermediate_string[f] + '\n')

    return(out_string.rstrip('\n'))


stdin = sys.stdin.read()
if len(sys.argv) < 2:
    print("Error: Missing args")

elif sys.argv[1] == "print-column" :
    if len(sys.argv) > 2:
        print(get_column(stdin, int(sys.argv[2]), '|', 9))
    else:
        print("Error: no column specified")


elif sys.argv[1] == "print-dirty-orgtbl" :
    print(arrange_in_columns(stdin, '|', 9))


else:
    print("Error: First arg must be a command, ie 'print-column'")

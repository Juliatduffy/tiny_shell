#!/usr/bin/python3

import subprocess
import re
import sys
import threading
import signal

target_process = re.compile(r'\d{1,6}\s+pts\/\d\s+\W\s+[0-9]:[0-9][0-9]\s+.\/mysplit 4')


def signal_handler(sig, frame):
 print('Ctrl+C Pressed. Exiting...')
 sys.exit(0)


def unique(sequence):
 seen = set()
 return [x for x in sequence if not (x in seen or seen.add(x))]


def replace_nums(input):
 i = 1
 out = input
 pattern = re.compile(r'(\([0-9]+\))')
 for num in unique(pattern.findall(out)):
  out = out.replace(num, "(PID-" + str(i) + ")")
  i += 1

 return out


def get_test(test_num, output, prefix = ''):
 test_name = f'{prefix}test{test_num:02}'
 out = subprocess.run(['make', test_name], stdout=subprocess.PIPE).stdout.decode('utf-8')

 if prefix == 'r':
  output[0] = out
 else:
  output[1] = out


def compare_prefix(ref, act, start, end):
 ref_prefix = replace_nums("\n".join(ref.splitlines()[start:end]))
 act_prefix = replace_nums("\n".join(act.splitlines()[start:end]))
 return ref_prefix == act_prefix


def get_process_list(input, occur=1):
 output = input.split("tsh> /bin/ps a")[occur]
 output = output.split("tsh>")[0]
 return output


def find_process(input, process_num = None, status = None, occur=1):
 ps = get_process_list(input, occur)
 occurances = target_process.findall(ps)
 has_process = False
 for line in occurances:
  if line.split()[2] != status:
   return -1

  if line.find(process_num) != -1:
   has_process = True

 return occurances if has_process else 0


def compare(ref, act, test_num):
 try:
  if (test_num <= 10 or test_num >= 14):
   return compare_prefix(ref, act, 2, None)

  if (test_num == 11):
   if not compare_prefix(ref, act, 1, 6):
    return False

   return find_process(act) == 0

  if (test_num == 12):
   if not compare_prefix(ref, act, 1, 8):
    return False

   pattern = re.compile(r'(\([0-9]+\))')
   process = pattern.findall(act.splitlines()[5])[0][1:-1]
   return find_process(ref, process, "T") == find_process(act, process, "T")

  if (test_num == 13):
   if not compare_prefix(ref, act, 1, 8):
    return False

   pattern = re.compile(r'(\([0-9]+\))')
   process = pattern.findall(act.splitlines()[5])[0][1:-1]
   if find_process(ref, process, "T") != find_process(act, process, "T"):
    return False

   return find_process(ref, None, None, 2) == find_process(act, None, None, 2)

 except:
  return False


signal.signal(signal.SIGINT, signal_handler)

try:
 skip = int(sys.argv[1])
except:
 skip = 0

for test_num in range(1,18):
 if test_num < skip:
  continue

 print(f'{test_num:02}...', end='')

 output = ["",""]
 t1 = threading.Thread(target=get_test, args=(test_num,output,'r'))
 t2 = threading.Thread(target=get_test, args=(test_num,output,''))

 t1.start()
 t2.start()

 t1.join()
 t2.join()

 ref = output[0]
 act = output[1]

 if not compare(ref, act, test_num):
  print('|__ERROR__|')
  print(f'Test number {test_num} does not match')
  print(f'Expected:\n{ref}')
  print(f'Actual:\n{act}')
  exit()

 print('PASSED')

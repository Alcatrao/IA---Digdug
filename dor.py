import subprocess, os, time

path = os.path.dirname(os.path.abspath(__file__))
contaDor = 0
while(True):
    contaDor += 1
    with open("scores.txt", 'a') as stream:
        stream.write("\n\n\n")
    print("\n\n\n")
    output = subprocess.run(['python3', os.path.join(path,'student_lvl41.py')])
    time.sleep(2)

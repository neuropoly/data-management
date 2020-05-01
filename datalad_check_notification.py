import os
import argparse
import smtplib                          
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

path_log = "/tmp/log_datalad_status.txt"

fromaddr = "alexandru.foias@polymtl.ca"
log_addr = "alexandrufoias@gmail.com"

def get_parameters():
    parser = argparse.ArgumentParser(description='This script is used to check the datalad dataset status')
    parser.add_argument("-d", "--path_datalad_dataset",
                        help="Path to datalad dataset",
                        required=True)                
    args = parser.parse_args()
    return args

def yes_or_no(question):
    reply = str(input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")

def main(path_datalad_dataset,path_log):
    os.system("(datalad status " + path_datalad_dataset + " >> " + path_log +") > /dev/null")

    if os.path.getsize(path_log) !=0:
        print('File is not empty')
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = log_addr
        msg['Subject'] = "[DATALAD] Changes in the datalad dataset:" + path_datalad_dataset.split('/')[-1]
        f = open(path_log,"r")
        body_part1 = "Here are the changes:\n"
        body_part2 = f.read()
        body_part3 = '\nPlease check & save the changes to Datalad.'
        msg.attach(MIMEText(body_part1+body_part2+body_part3, 'plain'))
            
        server = smtplib.SMTP('smtp.polymtl.ca', 587)
        text = msg.as_string()
        server.sendmail(fromaddr, log_addr, text)
        server.quit()
    if yes_or_no("Do you want to remove the log file ?"):
	    os.remove(path_log)

if __name__ == "__main__":
    args = get_parameters()
    main(args.path_datalad_dataset,path_log)

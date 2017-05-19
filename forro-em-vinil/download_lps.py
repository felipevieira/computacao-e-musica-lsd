from mega import Mega
import glob, os, shutil

def move_rar_files():
    files = glob.iglob(os.path.join(os.path.dirname(os.path.realpath(__file__)), "*.rar"))
    for file in files:
        if os.path.isfile(file):
            shutil.move(file, '/local/datasets/forro-em-vinil')    

email = '<mega.co email>'
password = 'mega.co password'

m = Mega.from_credentials(email, password)
url_files = open('tudo do forro em vinil.txt', 'r')

unsuccessful_downloads = open('unsuccessful_downloads.txt', 'w')
count=1

for url in url_files.readlines():
    try:
        print 'Downloading LP #%i: %s' % (count, url)
        m.download_from_url(url.strip())
    except:
        unsuccessful_downloads.write('%s\n' % url)
    finally:        
        # Send bulk to dataset dir
        if count%10 == 0:
            move_rar_files()
        count+=1

unsuccessful_downloads.close()
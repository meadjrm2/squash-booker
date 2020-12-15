# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 15:25:08 2020
@author: Rob Evans & John Mead

"""


import time
from bs4 import BeautifulSoup
from twill import browser
from datetime import datetime, timedelta

global username
global password
global desired_date
global desired_time
global login_url
global court_type
global preferred_court
global booking_url
global program_start_time
global booked

'''
class CourtUnavailableException(Exception):
    pass
class NoBookingSheetException(Exception):
    pass
'''

def log_in(login_url, username, password):
    print('Step 1 :Logging In to Booking System')
    print()
    #print('=====================================')
    #print('Booking a court on',desired_date,'at',desired_time)
    #print()
    #print('Logging in with Credentials:')
    #print('Username =', username)
    #print('Password =', password)
    #print('=====================================')
    #print()
    browser.go(login_url)
    if browser.find_link("Logout"):
        print ("Already logged in!")
    else:
        login_form = browser.form("1")
        username_field = browser.form_field(login_form, "username")
        password_field = browser.form_field(login_form, "password")
        username_field.value = username
        password_field.value = password
        browser.submit()
        if "denied" in browser.html.lower():   # error : TypeError: 'str' object is not callable : removed () after html - solved !
            raise Exception("Login failed!")
        else:
            print('Logged in successfully')
            print()

'''
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
SQUASH
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''

def squash_autobooker(target_datetime, timeout, interval):
    from datetime import datetime
    start = datetime.now()
    n=1
    max_no = 200
    while n < max_no:
        try:
            print('Squash Autobooker Booking attempt',n)
            book_squash(target_datetime)
            import datetime
            program_end_time = datetime.datetime.now()
            program_run_time = program_end_time - program_start_time
            microseconds = program_run_time .microseconds
            print('Squash Autobooker took', round(microseconds/1000000,3),'seconds to complete')
            n=n+1
            if booked == 1:
                break
            if datetime.now() > start + timeout:
                print ("Out of time, gave up at {}".format(datetime.now()))
                break
            time.sleep(interval.seconds)
        except Exception as e:
            print ('Problem :', e)# deleted ", e.message" as was causing an error
    if n == max_no:
        print ("Couldn't book a court after",n,"attemps : Someone got there first ?") 
            
            
def book_squash(target_datetime):
    global booked
    log_in(login_url, username, password)
    date_str = target_datetime.strftime('%d/%m/%Y')
    time_str = target_datetime.strftime('%H%M')
    time_str_print = target_datetime.strftime('%H:%M')
    print()
    print ("Step 2 : Navigating to booking sheets page")
    booking_url = login_url+'/bookings.asp'
    browser.go(booking_url)
    booking_sheet_link = browser.find_link(date_str)  
    if not booking_sheet_link:
        print("Could not find booking sheet for {}!".format(date_str))
    print()
    print('Step 3 : Navigating to Booking sheet for', date_str)
    browser.follow_link(booking_sheet_link)                                 #https://blackheathsquashclub.mycourts.co.uk/bookings.asp?st1=600&st2=2400&d=13
    print()
    print ("Step 4 : Attempting to book a squash court at {} on {}".format(time_str, date_str))
    soup = BeautifulSoup(browser.html, 'html.parser')  #removed () after html 
    
    #booking_link = None
    booked = 0
    n=1
    #Courts 1-4 : Acrylic
    courts = soup.findAll("div", {"class": "nested_column"})
    for div in courts: # for each court
        court_name = div.find("div", {"class": "courtname"} ).getText()
        print('-------------------------------------------')
        print('4.',n,': Trying Court :', court_name)
        print('-------------------------------------------')
        for court in div.findAll("div", {"class": "court_available"}): #only avaialble courts
            if court.getText().startswith(time_str):
                #initial booking sheet - book the court
                booking_url2 = court.find("a", {"class": "book_this_court"})['href'].replace(' ', '%20') 
                print('Step 5. Booking the court for', time_str_print)           #<a class="book_this_court" href="bookings_confirm.asp?st1=600&amp;st2=2400&amp;ctid=33684&amp;dt=12 December 2020&amp;tabID=0">book now</a>
                browser.follow_link(booking_url2)                           #https://blackheathsquashclub.mycourts.co.uk/bookings_confirm.asp?st1=600&st2=2400&ctid=33684&dt=12%20December%202020&tabID=0
                #confirm booking page
                print('Step 6. Confirming the court booking for', court_name, 'at', time_str_print, 'on', date_str)
                soup2 = BeautifulSoup(browser.html, 'html.parser')
                if soup2.find("div",{"class": "alert" }):
                    confirm_url = soup2.find_all('div', class_='alert')[0].find_all('a')[0].get('href').replace(' ', '%20') #class = alert
                else:
                    print()
                    print('=============================================================')
                    print('%%% Unable to book - too early ? Already have a booking ? %%%')
                    print('=============================================================')
                    print()
                    break
                if confirm_url:
                    browser.follow_link(confirm_url)
                    print()
                    print('=======================================================================')
                    print ('%%%  SUCCESS %%%  Tennis', court_name, 'booked for {} on {}'.format(time_str_print, date_str))
                    print('=======================================================================')
                    print()
                    booked = 1
                    break
                else:
                    print('Attempt',n,'Didn\'t manage to book court for {} {}'.format(date_str, time_str_print),'- trying the next available court')
                    n=n+1
            if booked == 1:
                break
        if booked == 1:
            break
    if booked == 0:
            print()
            print('Ran out of available courts and was not able to book any - so sorry')
            print()
    
    
    
    """
    #booking_link = None
    booked = 0
    for div in soup.findAll("div", {"class": "court_available"}):
        if div.getText().startswith(time_str):
            #initial booking sheet - book the court
            print('Found a court for', time_str)
            booking_url2 = div.find("a", {"class": "book_this_court"})['href'].replace(' ', '%20') 
            print()
            print('Booking the court for', time_str)
            #<a class="book_this_court" href="bookings_confirm.asp?st1=600&amp;st2=2400&amp;ctid=33684&amp;dt=12 December 2020&amp;tabID=0">book now</a>
            browser.follow_link(booking_url2)                            #https://blackheathsquashclub.mycourts.co.uk/bookings_confirm.asp?st1=600&st2=2400&ctid=33684&dt=12%20December%202020&tabID=0
            #confirm booking page
            print()
            print('Confirming the court booking for', time_str, 'on', date_str)
            soup = BeautifulSoup(browser.html, 'html.parser')
            confirm_url = soup.find_all('div', class_='alert')[0].find_all('a')[0].get('href').replace(' ', '%20')
            browser.follow_link(confirm_url)
            print()
            print('==============================================================================')
            print ("%%%  SUCCESS %%%  Squash Court Booked for {} on {}".format(time_str, date_str))
            print('==============================================================================')
            print()
            booked = 1
        
            if booked != 1:
                print('Didn\'t manage to book for {} {}'.format(date_str, time_str))
    """
    
'''
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
TENNIS
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''


def tennis_autobooker(target_datetime, timeout, interval):
    from datetime import datetime
    start = datetime.now()
    n=1
    max_no = 200
    while n < max_no:
        try:
            print()
            print(':::::::::::::::::::::::::::::::::::::')
            print('Tennis Autobooker Booking attempt',n)
            book_tennis(target_datetime, court_type)
            import datetime
            program_end_time = datetime.datetime.now()
            program_run_time = program_end_time - program_start_time
            microseconds = program_run_time .microseconds
            print('Tennis Autobooker took', round(microseconds/1000000,3),'seconds to complete')
            n=n+1
            print('4 Auto booker Booked =', booked)
            if booked == 1:
                break
            if datetime.now() > start + timeout:
                print ("Out of time, gave up at {}".format(datetime.now()))
                break
            time.sleep(interval.seconds)
        except Exception as e:
            print ('Problem :', e)# deleted ", e.message" as was causing an error
    if n == max_no:
        print ("Someone got there first") # deleted ", e.message" as was causing an error


def book_tennis(target_datetime, court_type):
    global booked
    log_in(login_url, username, password)
    date_str = target_datetime.strftime('%d/%m/%Y')
    time_str_print = target_datetime.strftime('%H:%M')
    time_str = target_datetime.strftime('%H%M')
    #taking the first 0 off for 08:00 and 09:00 (shows as 800 and 900 on booking sheets)
    if time_str[0] == '0':
        time_str = time_str[1]+time_str[2]+time_str[3]
    print()
    print ("Step 2 : Navigating to booking sheets page for",court_type,'courts')

    if court_type == 'clay':
        booking_url = login_url+'/bookings.asp?st1=600&st2=2400&d=0&tabID=223'
    if court_type == 'acrylic' :
        booking_url = login_url+'/bookings.asp'

    browser.go(booking_url)
    booking_sheet_link = browser.find_link(date_str)  
    if not booking_sheet_link:
        print("Could not find booking sheet for {}!".format(date_str))
    print()
    print('Step 3 : Navigating to Booking sheet for', date_str)
    browser.follow_link(booking_sheet_link)                                 #https://blackheathsquashclub.mycourts.co.uk/bookings.asp?st1=600&st2=2400&d=13
    print()
    if court_type == 'acrylic':
        preposition = 'an'
    if court_type == 'clay':
        preposition = 'a'
    print ('Step 4 : Attempting to book', preposition, court_type, 'court at {} on {}'.format(time_str_print, date_str))
    soup = BeautifulSoup(browser.html, 'html.parser')  #removed () after html 
    #booking_link = None
    booked = 0
    n=1
    #Courts 1-4 : Acrylic
    courts = soup.findAll("div", {"class": "nested_column"})
    for div in courts: # for each court
        court_name = div.find("div", {"class": "courtname"} ).getText()
        print('------------------')
        print('4.',n,': Trying Court :', court_name)
        print('------------------')
        for court in div.findAll("div", {"class": "court_available"}): #only avaialble courts
            if court.getText().startswith(time_str):
                #initial booking sheet - book the court
                booking_url2 = court.find("a", {"class": "book_this_court"})['href'].replace(' ', '%20') 
                print('Step 5. Booking the court for', time_str_print)           #<a class="book_this_court" href="bookings_confirm.asp?st1=600&amp;st2=2400&amp;ctid=33684&amp;dt=12 December 2020&amp;tabID=0">book now</a>
                browser.follow_link(booking_url2)                           #https://blackheathsquashclub.mycourts.co.uk/bookings_confirm.asp?st1=600&st2=2400&ctid=33684&dt=12%20December%202020&tabID=0
                #confirm booking page
                print('Step 6. Confirming the court booking for', court_name, 'at', time_str_print, 'on', date_str)
                soup2 = BeautifulSoup(browser.html, 'html.parser')
                if soup2.find("div",{"class": "alert" }):
                    confirm_url = soup2.find_all('div', class_='alert')[0].find_all('a')[0].get('href').replace(' ', '%20') #class = alert
                else:
                    print()
                    print('======================================================')
                    print('%%% Looks like you already have a booking that day %%%')
                    print('======================================================')
                    print()
                    break
                if confirm_url:
                    browser.follow_link(confirm_url)
                    print()
                    print('=======================================================================')
                    print ('%%%  SUCCESS %%%  Tennis', court_name, 'booked for {} on {}'.format(time_str_print, date_str))
                    print('=======================================================================')
                    print()
                    booked = 1
                    print('1 Booked =', booked)
                    break
                else:
                    print('Attempt',n,'Didn\'t manage to book court for {} {}'.format(date_str, time_str_print),'- trying the next available court')
                    n=n+1
            if booked == 1:
                print('2 Booked =', booked)
                break
        if booked == 1:
            print('3 Booked =', booked)
            break
    if booked == 0:
            print()
            print('Ran out of available courts and was not able to book any - so sorry')
            print()


def cancel_tennis_courts_to_avoid_fees():
    #++++++++++++++++++++++++++++++++++++++++++++++++
    import datetime
    cancel_date=datetime.date.today() + timedelta(days=0)
    #++++++++++++++++++++++++++++++++++++++++++++++++
    print ("Cancelling courts without opponents on {}".format(cancel_date.strftime('%A %d %B %Y')))
    log_in(login_url, username, password)
    my_bookings_url = login_url + '/my_bookings.asp'
    browser.go(my_bookings_url)
    soup = BeautifulSoup(browser.html, 'html.parser')    # removed () after html 
    bookings_table = soup.findAll("table", {"class":"form_table my_bookings"})
    cancelled_count = 0
    for booking in bookings_table:
        #rows = get_booking_table_rows()
        if int(cancel_date.strftime('%d')) < 10:
            cancel_date_to_use = cancel_date.strftime('%d') #str '09'
            cancel_date_to_use = cancel_date_to_use.replace('0','') #str '9'
        else:
            cancel_date_to_use = cancel_date.strftime('%d')
        if 'select opponent(s)' in str(booking) and cancel_date_to_use in str(booking):
            date = str(bookings_table[3]).split()[7] + ' ' +  str(bookings_table[3]).split()[8] + ' ' + str(bookings_table[3]).split()[9]  
            time = str(bookings_table[3]).split()[39]
            court = str(bookings_table[3]).split()[17] + ' ' + str(bookings_table[3]).split()[18].replace('</a></td>','')
            print('Unfilled booking found for',court,'on',date,'at',time)
            print()
            try:
                cancel_link = 'https://blackheath-ltc.mycourts.co.uk/bookings_cancel.asp?bid='+str(booking).split()[31].replace('id="cancel','').replace('"','')
                browser.go(cancel_link)
                print('Cancelled', court, 'on', date, 'at', time)
            except Exception as e:
                    print ("Failed to cancel court {} {}".format(e, booking))
            cancelled_count = cancelled_count + 1
    if cancelled_count == 0 :
            print ("No courts to cancel")
            
           
'''
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
RUN PROGRAM 
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
''' 




tennis_go = 'on'
squash_go = 'on'

# ----------------------------------------------
#if running on the cmd prompt:
    
# cd c:\Users\User\Python\Squash Booker
# python Rob_Squash_Court_Booker_Simple_V3.py
# Ctrl + C to stop prog 
# ----------------------------------------------
'''
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
BOOKING ROBOT
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''
squash_window_start = '11:59'
squash_window_stop = '12:01'
import datetime
today = datetime.date.today()
from datetime import datetime
prog_run_now = datetime.now()
from datetime import datetime
target_time = datetime.strptime(squash_window_start, '%H:%M').time() 
squash_start_time = datetime.combine(today, target_time)  

tennis_window_start = '05:59'
tennis_window_stop = '06:01'
import datetime
today = datetime.date.today()
from datetime import datetime
prog_run_now = datetime.now()
from datetime import datetime
target_time = datetime.strptime(tennis_window_start, '%H:%M').time() 
tennis_start_time = datetime.combine(today, target_time)  



#print()
#print('Booking',court,'court for',desired_time,'on', desired_date)
import datetime
program_start_time =  datetime.datetime.now()

if prog_run_now > tennis_start_time:
    if tennis_go == 'on':
        import datetime
        court_type = 'clay' #'acrylic'
        preferred_court = 5
        target_date_tennis = datetime.date.today() + timedelta(days=7)
        day = target_date_tennis.strftime('%A')
        if day == 'Monday':
            desired_time_tennis = '18:00'
        if day == 'Tuesday':
            desired_time_tennis = '19:00'
        if day == 'Wednesday':
            desired_time_tennis = '19:00'
        if day == 'Thursday':
            desired_time_tennis = '19:00'
        if day == 'Friday':
            desired_time_tennis = '13:00'
        if day == 'Saturday':
            desired_time_tennis = '13:00'
        if day == 'Sunday':
            desired_time_tennis = '13:00'
        if target_date_tennis >= datetime.date.today():
            from datetime import datetime
            target_time = datetime.strptime(desired_time_tennis, '%H:%M').time() 
            target_datetime = datetime.combine(target_date_tennis, target_time)        #datetime.datetime(2020, 12, 12, 18, 30)
            timeout=timedelta(minutes=5)
            interval=timedelta(seconds=1)
            login_url = 'https://blackheath-ltc.mycourts.co.uk'
            if court_type == 'Clay' or court_type == 'CLAY':
                court_type = 'clay'
            if court_type == 'Acrylic' or court_type == 'ACRYLIC':
                court_type = 'acrylic'
            #++++++++++++++++++++++
            username = "xxxxxy"
            password = "xxxxxy"
            #++++++++++++++++++++++
            tennis_autobooker(target_datetime, timeout, interval)
            #cancel_tennis_courts_to_avoid_fees()
        else:
            print('Requested date is in the past so can\'t book anything')
    else:
        print('Not proceeding with the tennis auto-booker')
        print()
else:
    print('It\'s too early to run the tennis auto-booker - this starts at',tennis_start_time)
    
    
if prog_run_now > squash_start_time:
    if squash_go == 'off':
        #preferred_court = 2
        import datetime
        target_date_squash = datetime.date.today() + timedelta(days=14)
        desired_time_squash = '19:30'
        if target_date_squash >= datetime.date.today():
            from datetime import datetime
            target_time = datetime.strptime(desired_time_squash, '%H:%M').time() 
            target_datetime = datetime.combine(target_date_squash, target_time)        #datetime.datetime(2020, 12, 12, 18, 30)
            timeout=timedelta(minutes=5)
            interval=timedelta(seconds=1)
            login_url = 'https://blackheathsquashclub.mycourts.co.uk'
            #++++++++++++++++++++++
            username = "xxxxxy"
            password = "xxxxxy"
            #++++++++++++++++++++++
            booked = 0
            squash_autobooker(target_datetime, timeout, interval)
        else:
            print('Requested date is in the past so can\'t book anything')
    else:
        print('Not proceeding with the squash auto-booker')
        print()
else:
    print('It\'s too early to run the squash auto-booker - this starts at',squash_start_time)






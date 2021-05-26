# parsing_ikea_il
 
<p>This project allows you to collect information about products from the <a href='https://www.ikea.co.il
'> www.ikea.co.il</a> website.</p>
<p>Script can be run by Window or Linux OS</p>
<p>
The scripts use the <a href='https://www.selenium.dev/selenium/docs/api/py/'> Selenium</a> library. 
The scripts are launched using a pipeline built on the <a href='https://github.com/spotify/luigi'>Luigi framework</a>. 
A <a href='https://github.com/eternnoir/pyTelegramBotAPI'>pyTelegramBotAPI library</a> is used for notifications (For messages to arrive,
you need to set your values of CHAT_ID and BOT_TOKEN. Look at telegram_notify.py file). 
Result of scripts working (.scv) will be in /data. To run scripts you need setup the python envieroment, requirements and start luigid. Look at the ikea_pipeline.py (below) for finding out of start script commands. 
Result of scripts working (.scv) will be in /data.</p>
The result of the work can be seen on the <a href='https://public.tableau.com/profile/alexander.feldman8264#!/vizhome/SearchIkeaILproducts/SearchIkeaIsraelProducts'>
Tableau dashboard</a>.

import mysql.connector

print('Connecting to mysql')

password = "Gp7V+F%8EL=g*-N3"
cnx = mysql.connector.connect(user='admin', password=password,
                              host='15.184.206.158',
                              database='shilengae')

                              
# 1. Location (needs ethiopia country)
# 2. user
# 3. category - Needs Root Category with Root form
# 4. ad

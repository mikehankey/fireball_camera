from crypt import Crypt

c = Crypt() 
a  = c.encrypt('12345')
print(a)
b = c.decrypt(a)
print(b)

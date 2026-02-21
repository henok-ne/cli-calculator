con=True
def add(x,y):
        print(x+y)
def  div(x,y):
        print(x/y)
def  sub(x,y):
        print(x-y)
def multi(x,y):
        print(x*y)
def main():
    while con==True:
            try:
                num1=int(input("enter the first number"))
                num2=int(input("enter the second number"))
                cho=input("enter the operation '+,-,*,/ or ex' ")
                
            except ValueError:
                print("Invalid input. Please enter numbers only.")
                continue
            except ZeroDivisionError:
                print("Error: Division by zero is not allowed.")
                continue
            if cho=="+":
                add(num1,num2)
            elif cho=="-":
                sub(num1,num2)
            elif cho=="/":
                div(num1,num2)
            elif cho=="*":
                multi(num1,num2)
            elif cho=="ex":
                break
            else:
                print("error")
con=True
def add(x,y):
        print(x+y)
def  div(x,y):
        print(x/y)
def  sub(x,y):
        print(x-y)
def multi(x,y):
        print(x*y)

while con==True:
        try:
            num1=int(input("enter the first number"))
            num2=int(input("enter the second number"))
            cho=input("enter the operation '+,-,*,/ or ex' ")
            
        except ValueError:
            print("Invalid input. Please enter numbers only.")
            continue
        except ZeroDivisionError:
            print("Error: Division by zero is not allowed.")
            continue
        if cho=="+":
            add(num1,num2)
        elif cho=="-":
            sub(num1,num2)
        elif cho=="/":
            div(num1,num2)
        elif cho=="*":
            multi(num1,num2)
        elif cho=="ex":
            break
        else:
            print("error")
if __name__ == "__main__":
    main()

let A = 20
let B = 40
let C = A + B * B

try
    C = C / 0
catch
    display "Error: Division by zero attempted but not allowed."
end

display "The result is "
display C
/*
func add(a, b)
    let A = 100 
    return a + b + A
end

let result = add(20, 40)
display "Result: "
display result
*/
func greet()
    display "Hello from Greet"
end

func car()
    let i = 20
    while i > 1
        display "I LOVE SOCA"
        i = i - 1
    end -- END WHILE LOOP
end -- END FUNC

let i = 1
while i < 10
    display "I Love you"
    if i == 6
        --greet()
    end
    i = i + 1
end

greet()

car()

display "Person class declared"

class Counter
    let value = 0

    func init(start)
        this.value = start
    end

    func set()
        this.value = this.value + 1
    end

    func get()
        return this.value
    end
   func addNum(a,b)
   this.value = this.value + a
       this.value = this.value + b
       display "Result is :", this.value
   end
end

let c = new Counter(10)
let b = new Counter(20)
c.set()
c.addNum(7,8)
b.addNum(7,8)
display c.get()

/*
-- Closures (lambda captures scope)
let factor = 3
let multiply = lambda x -> x * factor 
display multiply(7) 

let result = (3 + 4) * 2 ^ 3 % 5
if result > 0 and result < 100
    display "value is ", result
end
*/
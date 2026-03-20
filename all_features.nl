display "NOVALANG COMPLETE FEATURE TEST"

display "variable test"
let x = 10
let y = 5
display x
display y

display "arithmetic test"
let sum = x + y
let product = x * y
let power = x ^ y
let mod = x % y
display sum
display product
display power
display mod

display "operator precedence"
display 2 + 3 * 4
display (2 + 3) * 4

display "string"
let language = "NOVALANG"
display "Hello " + language

display "boolean test"
let t = true
let f = false
display t
display f

display "comparison operators"
display x > y
display x < y
display x >= y
display x <= y
display x == y
display x != y

display "logical operators"
display (5 > 3) and (2 < 4)
display not(5 == 3)

display "list test"
let lst = [1,2,3]
display lst
lst[1] = 5
display lst

display "if statement"
if x > y
    display "x greater than y"
else
    display "y greater than x"
end

display "while loop"
let i = 1
while i < 4
    display i
    i = i + 1
end

display "for loop"
for n = 1 to 3
    display n
end

display "function test"
func greet()
    display "Hello from function"
end
greet()

display "try catch test"
try let a = 10 / 0
catch
    display "division error"
end

display "range function"
display range(5)
display range(2,6)

display "enumerate function"
display enumerate([10,20,30])

display "class test"
class Person
end
display "Class defined"

display "comment test"
-- this is a single line comment
-- comments do not produce output

display "program finished"

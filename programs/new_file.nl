class MyClass
    let property = 42
    func getProperty() 
        return property
    end
end

let myObject = new MyClass()
let value = myObject.getProperty()
display "value is ", value
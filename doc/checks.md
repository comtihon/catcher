# Check - to check your variable
Short form:
```yaml
 - check: '{{ variable }}'
```
checks if `variable` equals to true.  
Long form:  
```yaml
 - check:
     equals: {the: '{{ variable }}', is: true}
```
Where `equals` it the operator form performing checks. 

## Operators for performing results checks
### Terminators
Terminators are operators which do checks and return value. They can't call other operators.  
__equals__- check if two values are equal.  
long form: `the` _source_ `is` _expected_.  
negative: `the` _source_ `is_not` _expected_.  
```yaml
- check: 
    and: 
        - equals: {the: '{{ list[0] }}', is: 'a'}
        - equals: {the: '{{ list[1] }}', is_not: 'b'}
        - equals: {the: '{{ list[2] > 2 }}', is_not: true}
```
__contains__ - check if list contains value or dict contains key.  
long form: `the` _element_ `in` _source_  
negative: `the` _element_ `not_in` _source_
```yaml
- check: 
    or: 
        - contains: {the: 'a', in: '{{ list }}'}
        - contains: {the: 'n', not_in: '{{ list }}'}
```

### Nodes
Nodes are operators, which call other operators and can aggregate results of their checks. 
Inner operators can be other nodes or terminators.    
__and__ - true if all inner operators return true.  
```yaml
- check: 
    and: 
        - contains: {the: 'a', not_in: '{{ list }}'}
        - equals: {the: '{{ list[1] }}', is_not: 'b'}
        - equals: {the: '{{ list[2] > 2 }}', is_not: true}
```
__or__ - true if any of the inner operators return true.  
```yaml
- check: 
    or: 
        - contains: {the: 'a', in: '{{ list }}'}
        - contains: {the: 'n', not_in: '{{ list }}'}
```
__any__ - same as or, but only one inner operator can be used.  
```yaml
any:
    of: [bar, baz]
    equals: 'baz'
```
__all__ - same as and, but only one inner operator can be used.  
```yaml
all: 
    of: [1,1]
    equals: 1
```
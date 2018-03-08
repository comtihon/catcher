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
__equal__- check if two values are equal.

__contains__ - check if list contains value or dict contains key.

### Nodes
Nodes are operators, which call other operators and can aggregate results of their checks. 
Inner operators can be other nodes or terminators.    
__and__ - true if all inner operators return true.  
__or__ - true if any of the inner operators return true.  
__any__ - same as or, but only one inner operator can be used.  
__all__ - same as and, but only one inner operator can be used.
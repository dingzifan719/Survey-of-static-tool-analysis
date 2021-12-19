# Survey-of-static-tool-analysis


## USAGE

### FORMAT
```
usage: Format.py [-h] -t {enre,understand,sourcetrail,depends} -e ENTITYINPUT
                 -d DEPENDENCYINPUT -p PROJECTNAME -o OUTPUT
```
```
eg:
python Format.py -t souretrail -e .\input\node.csv -d .\input\edge.csv -p halo -o .\halo
```

### DIFF OF DEPENDENCY
```
usage: dependency_diff.py [-h] -lt
                          {enre,understand,sourcetrail,depends,code2graph} -rt
                          {enre,understand,sourcetrail,depends,code2graph} -e
                          ENTITY -ld LEFT_DEPENDENCY -rd RIGHT_DEPENDENCY -p
                          PROJECTNAME -o OUTPUT
```

```
eg: 
python dependency_diff.py -lt enre -rt understand -e "./input/enre_understand_entity_output.json" -ld "./halo/enre_halo_dependency.json" -rd "./halo/understand_halo_dependency.json" -p halo -o .\halo\halo.json
```
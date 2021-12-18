# Survey-of-static-tool-analysis


## USAGE

### FORMAT
```
usage: Format.py [-h] -t {enre,understand,sourcetrail,depends} -e ENTITYINPUT
                 -d DEPENDENCYINPUT -p PROJECTNAME -o OUTPUT
Format.py: error: the following arguments are required: -t/--tool, -e/--entityInput, -d/--dependencyInput, -p/--projectname, -o/--output
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
dependency_diff.py: error: the following arguments are required: -lt/--left_tool, -rt/--right_tool, -e/--entity, -ld/--left_dependency, -rd/--right_dependency, -p/--projectname, -o/--output
```

```
eg: 
python dependency_diff.py -lt enre -rt understand -e "./input/enre_understand_entity_output.json" -ld "./halo/enre_halo_dependency.json" -rd "./halo/understand_halo_dependency.json" -p halo -o .\halo\halo.json
```
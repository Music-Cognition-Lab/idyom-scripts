# idyom-scripts

Miscellaneous scripts for working with IDyOM (Information Dynamics of Music): https://github.com/Music-Cognition-Lab/idyom

**Disclaimer: we cannot promise these scripts are all well-maintained and widely supported, use at your own risk!**

---

Python scripts (tested on v3.8.1):

- `checkbioi.py` : utility to identify cases where BIOIs (basic inter onset intervals) derived by IDyOM are not equal to the difference in ONSET between successive events - this can cause model errors.
- `exportdb.py` : class that exports IDyOM's database as a Pandas `DataFrame`.

Lisp scripts (note that you may need to run `(clsql:enable-sql-reader-syntax)` to allow `clsql` syntax):

- `fix-bioi.lisp` : functions for fixing temporal structure in a dataset (onset, ioi, dur and deltast).
- `remove-duplicates.lisp` : functions for removing duplicates from a dataset.

# 



# 

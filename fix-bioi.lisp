#.(clsql:locally-enable-sql-reader-syntax)

(defun fix-bioi (dataset-id &key (dry-run t))
  "Assumes onset is correct and updates bioi to match."
  (dotimes (c (idyom-db:count-compositions dataset-id))
    (dotimes (e (idyom-db:count-events dataset-id c))
      #.(clsql:locally-enable-sql-reader-syntax)
      (let* ((where-clause [and [= [dataset-id] dataset-id] [= [composition-id] c] [= [event-id] e]])
             (previous-onset (car (clsql:select [onset] :from [mtp-event] 
                                                :where [and [= [dataset-id] dataset-id] [= [composition-id] c] [= [event-id] (1- e)]]
                                                :flatp t)))
             (onset (car (clsql:select [onset] :from [mtp-event] :where where-clause :flatp t)))
             (bioi (car (clsql:select [bioi] :from [mtp-event] :where where-clause :flatp t)))
             (value (if (= e 0) 0 (- onset previous-onset))))
        (when (and onset previous-onset (not (= bioi value)))
          (format t "~&~A ~A ~A ~A ~A ~A~%" c e previous-onset onset value bioi)
          (unless dry-run
            (clsql:update-records [mtp-event] :av-pairs `((bioi ,value)) :where where-clause)))))))

(defun fix-bioi-dur-deltast (dataset-id &key (dry-run t))
  "Assumes onset and deltast are correct and updates bioi and dur to match."
  (dotimes (c (idyom-db:count-compositions dataset-id))
    (let ((bioi 0))
      (dotimes (e (idyom-db:count-events dataset-id c))
        (let* ((where-clause [and [= [dataset-id] dataset-id] [= [composition-id] c] [= [event-id] e]])
               (onset (car (clsql:select [onset] :from [mtp-event] :where where-clause :flatp t)))
               (old-dur (car (clsql:select [dur] :from [mtp-event] :where where-clause :flatp t)))
               (old-deltast (car (clsql:select [deltast] :from [mtp-event] :where where-clause :flatp t)))
               (old-bioi (car (clsql:select [bioi] :from [mtp-event] :where where-clause :flatp t)))
               (next-onset (car (clsql:select [onset] :from [mtp-event]
                                              :where [and [= [dataset-id] dataset-id] [= [composition-id] c] [= [event-id] (1+ e)]]
                                              :flatp t)))
               (next-bioi (car (clsql:select [bioi] :from [mtp-event]
                                             :where [and [= [dataset-id] dataset-id] [= [composition-id] c] [= [event-id] (1+ e)]]
                                             :flatp t)))
               (next-deltast (car (clsql:select [deltast] :from [mtp-event]
                                             :where [and [= [dataset-id] dataset-id] [= [composition-id] c] [= [event-id] (1+ e)]]
                                             :flatp t)))
               (new-next-bioi (when next-onset (- next-onset onset)))
               (new-dur (when next-onset (- new-next-bioi next-deltast))))
          (when (and onset next-onset)
            ;; (format t "~&~A ~A ~A ~A ~A ~A~%" c e onset next-onset bioi new-dur)
            (unless (and (= old-bioi bioi) (= old-dur new-dur))
              (format t "~&~A ~A: ~A ~A ~A ~A~%" c e old-dur old-bioi next-deltast next-bioi)
              (format t "~&~A ~A: ~A ~A ~A ~A~%" c e new-dur bioi     next-deltast new-next-bioi))
            (unless dry-run
              (clsql:update-records [mtp-event] :av-pairs `((bioi ,bioi) (dur ,new-dur)) :where where-clause)))
          (setf bioi new-next-bioi))))))

(defun fix-onset (dataset-id &key (dry-run t))
  "Assumes bioi, deltast and duration are correct and updates onset to match bioi."
  (dotimes (c (idyom-db:count-compositions dataset-id))
    (let ((previous-bioi 0)
          (previous-onset 0))
      (dotimes (e (idyom-db:count-events dataset-id c))
        (let* ((where-clause [and [= [dataset-id] dataset-id] [= [composition-id] c] [= [event-id] e]])
               (old-onset (car (clsql:select [onset] :from [mtp-event] :where where-clause :flatp t)))
               (old-dur (car (clsql:select [dur] :from [mtp-event] :where where-clause :flatp t)))
               (old-deltast (car (clsql:select [deltast] :from [mtp-event] :where where-clause :flatp t)))
               (old-bioi (car (clsql:select [bioi] :from [mtp-event] :where where-clause :flatp t)))
               (new-onset (if (= previous-bioi 0) old-onset (+ previous-onset old-bioi))))
          (when (and old-onset new-onset)
            (format t "~&~A ~A ~A ~A ~A ~A ~A~%" c e previous-onset old-onset old-bioi old-dur old-deltast)
            (format t "~&~A ~A ~A ~A ~A ~A ~A~%" c e previous-onset new-onset old-bioi old-dur old-deltast))
          (unless dry-run
            (clsql:update-records [mtp-event] :av-pairs `((onset ,new-onset)) :where where-clause))
          (setf previous-bioi old-bioi
                previous-onset new-onset))))))

#.(clsql:restore-sql-reader-syntax-state)

        
            

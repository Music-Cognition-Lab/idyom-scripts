;; remove duplicates

(defun remove-duplicate-compositions (dataset-id new-dataset-id n viewpoint)
  "Copy dataset <dataset-id> to a new dataset specified by
  <new-dataset-id> with duplicates removed. <n> and <viewpoint> are
  passed to FIND-DUPLICATE-COMPOSITIONS." 
  (multiple-value-bind (d i)
      (find-duplicate-compositions dataset-id nil n viewpoint)
    (declare (ignore d))
    (let* ((i (reduce #'append (mapcar #'cdr i)))
           (description (utils:string-append (idyom-db:get-description dataset-id) (format nil " (duplicates removed: ~A ~A)." n viewpoint))))
      (idyom-db:copy-datasets new-dataset-id (list dataset-id) description (list i)))))

(defun find-duplicate-compositions (dataset-id composition-ids n viewpoint)
  "A composition is considered a duplicate if it the first <n>
viewpoint elements match for the supplied <viewpoint>."
  (let ((count (idyom-db:count-compositions dataset-id))
        (melodies (make-hash-table))
        (descriptions (make-hash-table))
        (result nil))
    (dotimes (i count)
      ;;(print i)
      (let* ((intervals (viewpoints:viewpoint-sequence
                         (viewpoints:get-viewpoint viewpoint)
                         (md:get-event-sequence dataset-id i))))
        (setf (gethash i melodies) intervals)
        (setf (gethash i descriptions) (idyom-db:get-description dataset-id i))))
    (dotimes (i (if (null composition-ids) count composition-ids))
      (let ((duplicates nil))
        (dotimes (j count)
          (unless (= i j)
            ;;(print (list i j))
            (let* ((si (gethash i melodies))
                   (sj (gethash j melodies))(n (min n (length si) (length sj)))
                   (intervals (subseq si 0 n))
                   (intervals2 (subseq sj 0 n)))
              (if (equalp intervals intervals2)
                  (push j duplicates)))))
        (unless (null duplicates)
          (push (list i duplicates) result))))
    (setf result (mapcar #'(lambda (x) (cons (car x) (cadr x))) result))
    (setf result (mapcar #'(lambda (x) (sort x #'<)) result))
    (setf result (remove-duplicates result :test #'equal))
    (setf result (sort result #'< :key #'car))
    (values (mapcar #'(lambda (x)
                        (mapcar #'(lambda (y)
                                    (gethash y descriptions))
                                x))
                    result)
            result)))

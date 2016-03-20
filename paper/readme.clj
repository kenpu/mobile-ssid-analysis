;; we have a hierarchy
;;
;;
;; Segmentation is done by looking at the dissimilarity of a cluster.
;; The dissimilarity looks like the children
;; (C1, C2)
;; dissim * dt

(defn dissim [C]
  (if (leaf? C)
    (minsim C)
    (let [[C1 C2] (children C)
          ds1 (dissim C1)
          ds2 (dissim C2)
          ds3 (dissim (union C1 C2))]
      (max ds1 ds2 ds3))))

;; reject single null readings
;;


            A
         /     \
        C       D
       / \     / \
      X   Y   U   V

(defn prev [v]
  (cond
        (nil?)   nil
        (root?)  nil
        (left?)  (-> v parent prev right))
        (right?) (-> v parent left))

(defn next [v]
  (condp
        (nil?)   nil
        (root?)  nil
        (left?)  (-> v parent right))
        (right?) (-> v parent next left))

(defn eliminate? [v]
  (let [p (prev v)
        n (next v)]
    (and
         (short-duration? v)
         (far? p v)
         (far? n v)
         (close? p n))))


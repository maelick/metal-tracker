(ns metaltracker.core
  (:require [pl.danieljanus.tagsoup :as xml]
            [clojure.string :as str]))

(def root-url "http://en.metal-tracker.com")

(defn get-elements-node
  "Returns a sequence of elements from a hierachy matching a specified tag.
   If specified, tags must also have an attribute which may also be of a
   specified value."
  ([tree tag]
     (if (or (char? tree) (empty? tree))
       []
       (let [res (map (fn [t] (get-elements-node t tag)) (xml/children tree))]
         (if (= (xml/tag tree) tag)
           (reduce concat (concat [[tree]] res))
           (reduce concat res)))))
  ([tree tag att]
     (filter
      (fn [t] (contains? (xml/attributes t) att))
      (get-elements-node tree tag)))
  ([tree tag att value]
     (filter
      (fn [t] (= (att (xml/attributes t)) value))
      (get-elements-node tree tag))))

(defn get-elements
  "Returns a sequence of elements from a sequeucen of hierachies matching a
   specified tag. If specified, tags must also have an attribute which may
   also be of a specified value."
  ([trees tag]
     (reduce concat (map (fn [t] (get-elements-node t tag)) trees)))
  ([trees tag att]
     (reduce concat (map (fn [t] (get-elements-node t tag att)) trees)))
  ([trees tag att value]
     (reduce concat (map (fn [t] (get-elements-node t tag att value)) trees))))

(defn parse-basic-data
  ""
  [meta-data]
  (let [[tag value] (xml/children meta-data)]
    [(keyword (first (str/split (str/lower-case (first (xml/children tag)))
                                #":"))) value]))

;; TODO: make map

(defn parse-meta-data
  ""
  [meta-data]
  (map parse-basic-data (filter (fn [t] (not-empty (xml/children t))) meta-data)))

(defn get-torrent
  ""
  [tree]
  (let [title (:title (xml/attributes
                       (first (get-elements-node tree :img :class "updates"))))
        raw-meta-data (get-elements (get-elements-node tree :ul :class
                                                       "basic_data") :li)
        link (:href (xml/attributes (first (get-elements-node tree :a))))]
    {:title title, :link link, :meta-data (parse-meta-data raw-meta-data)}))

(defn parse-page
  "Get & parse torrents from a given page."
  [page]
  (map get-torrent (get-elements-node (xml/parse page) :div :class "update")))

(defn foo
  "I don't do a whole lot."
  [x]
  (println x "Hello, World!"))

(defn -main
  "Main function."
  [& args]
  (doseq [torrent (parse-page root-url)]
    (println torrent)))
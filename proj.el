;;; -*- lexical-binding: t; -*-
(setq name "pybindfs")
(setq proj-dir (expand-file-name default-directory))
(setq src (file-name-concat proj-dir "src" name))

(message "proj-dir:%s" proj-dir)
(setenv "PYTHONPATH"
	(concat
	 (file-name-concat proj-dir src)
	 ":"
	 (file-name-concat proj-dir "tests")))
(message "env:%s" (getenv "PYTHONPATH"))

(find-file (file-name-concat src (concat name ".py")))

;;; Directory Local Variables
;;; For more information see (info "(emacs) Directory Variables")

((python-mode
  (eval setq flycheck-python-pylint-executable
        (concat (locate-dominating-file buffer-file-name ".dir-locals.el")
                "run-pylint"))
  (fill-column . 119)))

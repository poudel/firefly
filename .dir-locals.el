;; concat because sometimes (buffer-file-name) returns nil which string-match does not like
((nil (eval . (if (string-match ".py$" (concat (buffer-file-name) ""))(blacken-mode)))))

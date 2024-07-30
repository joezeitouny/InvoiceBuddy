## 0.2.8 (2024-07-30)

* Fixed an issue where mark proposal as accepted was generating an internal server error
* Version bump to 0.2.8

## 0.2.7 (2024-07-30)

* Fixed an issue where the stats html page wasn't correctly loaded
* UI Improvements
* Version bump to 0.2.7

## 0.2.6 (2024-07-30)

* Fixed an issue where the pie chart data was not correctly computed
* Version bump to 0.2.6

## 0.2.5 (2024-07-29)

* Fixed an issue where multiline content in the description field of invoices and proposals wasn't correctly rendered
* Added search and filtering capabilities to past invoicesAdded Stats page
* Added search and filtering capabilities to past proposals
* Added Stats page
* UI Improvements
* Version bump to 0.2.5

## 0.2.4 (2024-07-26)

* UI Improvements
* Version bump to 0.2.4

## 0.2.3 (2024-07-26)

* Reduced the image size for the seller logo in the invoice and proposal templates
* Added button to download configuration file
* Improved handling of uploading seller logo and configuration files
* Fixed typo in the CHANGELOG
* Version bump to 0.2.3

## 0.2.2 (2024-07-25)

* Added support for decimals in the quantity field (when adding invoice / proposal items)
* Fixed an issue where form fields validation weren't cleared before presenting the form
* Version bump to 0.2.2

## 0.2.1 (2024-07-24)

* Page data now refreshes after adding customer / item / invoice / proposal to reflect the newly added entry
* Version bump to 0.2.1

## 0.2.0 (2024-07-23)

* Added cutomers model
* Canceled invoices now generate credit invoices
* Seller logo is now also stored in the tmp directory so that when the application is updated the previously uploaded seller logo remains
* Version bump to 0.2.0

## 0.1.4 (2024-07-22)

* UI Layout improvements
* Added ability to duplicate invoices 
* Added ability to duplicate proposals
* Fixed an issue where autocomplete items on invoices and proposals wasn't working properly
* Version bump to 0.1.4

## 0.1.3 (2024-07-22)

* UI Layout improvements
* Version bump to 0.1.3

## 0.1.2 (2024-07-19)

* Added a confirmation modal for deleting items
* Uploaded seller logo is now visible on the configuration screen
* UI Layout improvements
* Added form field validation to the edit item form
* Added ability to update items
* Version bump to 0.1.2

## 0.1.1 (2024-07-18)

* Multilines are now better handled when viewing items
* Version bump to 0.1.1

## 0.1.0 (2024-07-18)

* Moved database storage to the tmp_path location
* Multilines are now better handled when generating invoices / proposals
* Fixed the navigation bar toggler button which wasn't working on smaller screens
* Version bump to 0.1.0

## 0.0.3 (2024-07-18)

* Fixed issue with uploading seller logo
* Version bump to 0.0.3

## 0.0.2 (2024-07-18)

* Updated Flask version requirement
* Version bump to 0.0.2

## 0.0.1 (2024-07-18)

* Initial release
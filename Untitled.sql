SELECT 
    'Person with ID=' || p.PERSON_ID || ' appeared in Camera at  ' || to_char(img.TIMERECORDED, 'DD/MM/YYYY  HH24:MI:SS.FF ') as "Reports"
FROM PEOPLE p JOIN EMP_IMG ei ON (p.Person_ID = ei.Person_ID)
    join IMAGES img on (img.Img_ID=ei.Img_ID)
order by
    img.TIMERECORDED desc;
Select * from IMAGES;
Select * from PEOPLE;

SELECT * FROM EMP_IMG;
SELECT 
    * 
FROM EMP_IMG
WHERE PERSON_ID is not null;